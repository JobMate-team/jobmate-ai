from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
import os
import json
from textwrap import dedent

from dotenv import load_dotenv
from openai import OpenAI

# 🔹 RAG 관련 import
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# .env에서 OPENAI_API_KEY 읽기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

client = OpenAI(api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)


# FAISS 벡터 DB 준비


def build_faiss_from_json(folder_path: str = "./embedding",
                          index_path: str = "faiss_index") -> None:
    """
    DevB가 만든 JSON 파일들(question_templates, answer_patterns, 등)을 읽어서
    FAISS 벡터 DB를 한 번 생성하는 함수.
    """
    docs: List[Document] = []

    filenames = [
        "question_templates.json",
        "answer_patterns.json",
        "competency_rubrics.json",
        "model_answers.json",
    ]

    for filename in filenames:
        filepath = os.path.join(folder_path, filename)
        if not os.path.exists(filepath):
            print(f" 파일을 찾을 수 없음: {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            items = json.load(f)
            # 각 item은 {"page_content": "...", "metadata": {...}} 형태라고 가정
            for item in items:
                docs.append(
                    Document(
                        page_content=item["page_content"],
                        metadata=item.get("metadata", {}),
                    )
                )

    if not docs:
        raise ValueError("임베딩에 사용할 문서가 없습니다. JSON 파일을 확인하세요.")

    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(index_path)
    print("FAISS 벡터 DB 생성 완료")


def load_vectorstore(index_path: str = "faiss_index") -> FAISS:
    if not os.path.exists(index_path):
        build_faiss_from_json()
    db = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
    print("FAISS 벡터 DB 로드 완료")
    return db


# 앱 시작 시 한 번만 로드 (전역)
vectorstore = load_vectorstore()


async def get_rag_context(
    job: str,
    company: str,
    question: str,
    answer: str,
    k: int = 4,
) -> Tuple[str, List[str]]:
    """
    질문/답변/직무/회사 정보를 기반으로 FAISS에서 유사 문서를 검색하고,
    - GPT에 넣을 컨텍스트 문자열
    - 각 문서의 'source' 같은 메타데이터 리스트
    를 반환.
    """
    query = f"{question}\n\n{answer}\n\n직무: {job}, 회사: {company}"

    docs = vectorstore.similarity_search(query, k=k)

    context_texts: List[str] = []
    sources: List[str] = []

    for doc in docs:
        context_texts.append(doc.page_content)

        meta = doc.metadata or {}
        # DevB JSON에 들어 있는 키 중 하나를 출처로 사용
        source = (
            meta.get("source")
            or meta.get("question_id")
            or meta.get("pattern_id")
            or meta.get("competency_id")
            or meta.get("id")
            or ""
        )
        sources.append(str(source))

    context = "\n\n---\n\n".join(context_texts)
    return context, sources



# 1. 요청/응답 모델 정의


class FeedbackRequest(BaseModel):
    job: str
    company: str
    question: str
    answer: str

class FeedbackResponse(BaseModel):
    summary: str
    logic: str
    concreteness: str
    fit: str
    delivery: str
    next_tips: List[str]
    example_answer: str
    retrieved_sources: List[str]



# 2. 프롬프트 정의


SYSTEM_PROMPT = """
당신은 한국어를 사용하는 인사담당자이자 면접 코치입니다.

지원자의 답변을 다음 기준으로 평가합니다.
- 논리성: 말의 흐름, 구조, 핵심 메시지가 명확한지
- 구체성: 경험, 수치, 기간, 역할 등 구체적인 정보가 있는지
- 직무 적합성: 답변이 지원 직무와 잘 연결되는지
- 전달력: 면접 상황(1~2분 답변)에 맞게 핵심이 잘 전달되는지

지원자가 바로 다음 연습에 활용할 수 있도록
'무엇을 어떻게 고쳐야 하는지'를 구체적으로 제안하세요.
막연한 칭찬보다 행동 지침에 가까운 피드백을 선호합니다.
"""

def build_user_prompt(
    job: str,
    company: str,
    question: str,
    answer: str,
    context_docs: str = ""
) -> str:
    job_desc = job or "특정 직무 정보가 없습니다. 일반적인 면접 역량 기준으로 평가해 주세요."
    company_desc = company or "특정 회사 정보는 제공되지 않았습니다."

    context_part = context_docs if context_docs else "별도의 참고 자료는 제공되지 않았습니다."

    return dedent(f"""
    [직무 정보]
    {job_desc}

    [회사 정보]
    {company_desc}

    [문서 컨텍스트 (참고 자료)]
    {context_part}

    [면접 질문]
    {question}

    [지원자의 답변]
    {answer}

    [요청사항]
    1. 위 답변에 대해 피드백을 제공해주세요.
       - 어떤 점이 좋고 어떤 점이 부족한지 서술
       - 필요한 경우 개선 제안을 포함하세요

    2. 해당 답변을 STAR 구조로 분석하여 각 요소별로 점수를 매기고 코멘트를 작성해주세요.
       - 예시:
         - Situation: 3/5 - 배경 설명이 모호함
         - Task: 4/5 - 목표가 명확하게 표현됨
         - Action: 2/5 - 구체적인 행동 설명이 부족함
         - Result: 3/5 - 성과가 뚜렷하지 않음

    3. 개선된 답변(모범답변)을 STAR 구조에 맞춰 다시 작성해주세요.
       - 각 단계별로 구분해서 작성해주세요.

    위 정보를 바탕으로, 아래 JSON 형식으로만 답변해 주세요.

    ```json
    {{
      "summary": "전반 평가 2~3문장",
      "logic": "논리성에 대한 피드백 3~5문장",
      "concreteness": "구체성에 대한 피드백 3~5문장",
      "fit": "직무 적합성에 대한 피드백 3~5문장",
      "delivery": "전달력에 대한 피드백 3~5문장",
      "next_tips": [
        "다음 연습 시 신경 쓸 점 1",
        "다음 연습 시 신경 쓸 점 2",
        "다음 연습 시 신경 쓸 점 3"
      ],
      "example_answer": "개선된 예시 답변(8~12문장)",
      "retrieved_sources": []
    }}
    ```

    설명 문장은 쓰지 말고, 위 JSON만 반환하세요.
    """)



# 3. GPT 호출 함수


def call_gpt(job: str, company: str, question: str, answer: str, context_docs: str = "") -> str:
    user_prompt = build_user_prompt(job, company, question, answer, context_docs)

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",  # 필요에 따라 모델 변경 가능
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    content = resp.choices[0].message.content
    return content



# 4. JSON 파서


def parse_feedback(raw: str) -> FeedbackResponse:
    cleaned = raw.strip()

    # ```json ... ``` 감싸진 경우 제거
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except Exception:
        # JSON 파싱 실패 시: raw 전체를 summary에 넣고 나머지는 기본값
        return FeedbackResponse(
            summary=cleaned[:500],
            logic="",
            concreteness="",
            fit="",
            delivery="",
            next_tips=[],
            example_answer="",
            retrieved_sources=[],
        )

    summary = data.get("summary", "")
    logic = data.get("logic", "")
    concreteness = data.get("concreteness", "")
    fit = data.get("fit", "")
    delivery = data.get("delivery", "")
    next_tips = data.get("next_tips", [])
    example_answer = data.get("example_answer", "")
    retrieved_sources = data.get("retrieved_sources", [])

    # 타입 방어: next_tips / retrieved_sources 가 문자열로 올 수도 있음
    if isinstance(next_tips, str):
        next_tips = [next_tips]
    if not isinstance(next_tips, list):
        next_tips = []

    if isinstance(retrieved_sources, str):
        retrieved_sources = [retrieved_sources]
    if not isinstance(retrieved_sources, list):
        retrieved_sources = []

    return FeedbackResponse(
        summary=summary,
        logic=logic,
        concreteness=concreteness,
        fit=fit,
        delivery=delivery,
        next_tips=next_tips,
        example_answer=example_answer,
        retrieved_sources=retrieved_sources,
    )



# 5. FastAPI 엔드포인트 /답변 테스트용 fast api


app = FastAPI()

@app.post("/ai-feedback", response_model=FeedbackResponse)
async def ai_feedback(request: FeedbackRequest):
    # 1) RAG로 컨텍스트 + 출처 가져오기
    try:
        context_docs, sources = await get_rag_context(
            request.job,
            request.company,
            request.question,
            request.answer,
        )
    except Exception as e:
        print(" RAG 에러, 컨텍스트 없이 진행:", e)
        context_docs = ""
        sources = []

    # 2) GPT 호출
    raw = call_gpt(
        job=request.job,
        company=request.company,
        question=request.question,
        answer=request.answer,
        context_docs=context_docs,
    )

    # 3) JSON 파싱
    feedback = parse_feedback(raw)

    # 4) 출처 정보 덮어쓰기
    feedback.retrieved_sources = sources

    return feedback
