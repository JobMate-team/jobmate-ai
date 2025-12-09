# 새로운 검색 규칙 기반 API 엔드포인트
from fastapi import Body
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
from typing import Optional
import logging
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


def build_faiss_from_json(folder_path: str = "src/embedding",
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
        "answer_templates.json",
        "company_values.json",
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
    job_group: str,
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
    query = dedent(f"""
{question}
{answer}

직군: {job_group}
직무: {job}
회사: {company}

# 회사 인재상 우선 검색을 위한 의도적 부스팅 키워드
[{company} 인재상 핵심가치 회사가 원하는 인재상 핵심역량 기업문화]

""")

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



# 기존 피드백 요청 모델 (기존 엔드포인트 호환)

class FeedbackRequest(BaseModel):
    job_group: str
    job: str
    company: str
    question: str
    answer: str
    standard_question: str = "n"  # "y" or "n"
    question_id: str = None        # standard_question=="y"일 때만 사용

# 새로운 질문 랜덤 추출 요청 모델
class RandomQuestionRequest(BaseModel):
    q_list: list[str]  # 예: ["tech", "tenacity", ...]
    count: int         # 각 타입별 추출 개수

# 새로운 질문 랜덤 추출 응답 모델
class RandomQuestionGroup(BaseModel):
    question_type: str
    questions: list[dict]  # 각 질문: {"page_content": ..., "metadata": {...}}

class RandomQuestionResponse(BaseModel):
    groups: list[RandomQuestionGroup]

class FeedbackResponse(BaseModel):
    company_values: str
    summary: str
    logic: str
    concreteness: str
    fit: str
    delivery: str
    next_tips: List[str]
    example_answer: str
    retrieved_sources: List[str]



class SearchDocumentsRequest(BaseModel):
    job_family: str
    question: str
    answer: str
    top_k: int = 3

class SearchDocumentsResponse(BaseModel):
    top_question_docs: list
    top_answer_docs: list
    competency_docs: list
    answer_pattern_docs: list

# 구조화된 피드백 요청/응답 (마크다운 문자열 반환)
class StructuredFeedbackRequest(BaseModel):
    company: str | None = None
    job_family: str
    question: str
    answer: str
    top_k: int = 3
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
    0. 만약 req.company가 비어 있거나 company_block이 비어 있다면:
    - 회사 인재상과 관련된 모든 내용을 절대 생성하지 말아주세요.
    - 회사와 관련된 조언, 요약, 비교, 평가 등을 절대 언급하지 말아주세요

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
      "company_values": "기업 인재상 요약 2~3문장 + 현재 인재상이 요구하는 방향으로 면접자가 어떤 식으로 답변을 구성하면 좋을지 구체적으로 제시하는 코멘트 (3~5문장)",
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
            company_values=cleaned[:500],
            summary=cleaned[:500],
            logic="",
            concreteness="",
            fit="",
            delivery="",
            next_tips=[],
            example_answer="",
            retrieved_sources=[],
        )
    company_values = data.get("company_values", "")
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
        company_values=company_values,
        summary=summary,
        logic=logic,
        concreteness=concreteness,
        fit=fit,
        delivery=delivery,
        next_tips=next_tips,
        example_answer=example_answer,
        retrieved_sources=retrieved_sources,
    )

# 5. 기업 인재상
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# -- 회사 인재상 로딩 유틸리티 ------------------------------------------------

# def load_company_values(path: str = "./src/embedding/company_values.json") -> list:
#     """
#     company_values.json 파일을 리스트로 읽어 반환한다.
#     파일이 없거나 파싱 실패 시 빈 리스트 반환.
#     """
#     if not os.path.exists(path):
#         logger.warning(f"company_values 파일을 찾을 수 없음: {path}")
#         return []

#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#             if isinstance(data, list):
#                 return data
#             else:
#                 # 파일이 dict 형태로 저장된 경우(구조가 다르면 이걸 처리)
#                 logger.warning(f"{path}의 형태가 list가 아님. 현재 타입: {type(data)}")
#                 # 만약 dict로 {company_name: page_content} 형태라면 변환할 수 있으나
#                 # 우선 빈 리스트 반환해서 안전하게 동작하도록 함
#                 return []
#     except Exception as e:
#         logger.exception("company_values.json 로드 중 오류 발생:")
#         return []



def load_company_values(path: str = "./src/embedding/company_values.json") -> list:
    """
    company_values.json 파일을 리스트로 읽어 반환한다.
    파일이 없거나 파싱 실패 시 빈 리스트 반환.
    """
    if not os.path.exists(path):
        logger.warning(f"company_values 파일을 찾을 수 없음: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                # 파일이 dict 형태로 저장된 경우(구조가 다르면 이걸 처리)
                logger.warning(f"{path}의 형태가 list가 아님. 현재 타입: {type(data)}")
                # 만약 dict로 {company_name: page_content} 형태라면 변환할 수 있으나
                # 우선 빈 리스트 반환해서 안전하게 동작하도록 함
                return []
    except Exception as e:
        logger.exception("company_values.json 로드 중 오류 발생:")
        return []

# 전역 변수로 한 번만 로드 (앱 시작 시)
company_values_data: list = load_company_values()


def get_company_values(company: str) -> Optional[str]:
    """
    company (회사명 혹은 company_id)에 매칭되는 item의 page_content를 반환.
    일치하는 항목이 없으면 None 반환.
    company_values_data는 모듈 로드 시 이미 초기화되어 있음.
    
    만약 req.company가 비어 있거나 company_block이 비어 있다면:
    - 회사 인재상과 관련된 모든 내용을 절대 생성하지 말아주세요.
    - 회사와 관련된 조언, 요약, 비교, 평가 등을 절대 언급하지 말아주세요.

    """
    if not company:
        return None

    # 안전성: 회사 데이터가 비어 있으면 바로 None 반환
    if not company_values_data:
        return None

    for item in company_values_data:
        # item은 {"page_content": "...", "metadata": {...}} 형태라고 가정
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata") or {}
        # 매칭 조건: company_name 또는 company_id
        if meta.get("company_name") == company or meta.get("company_id") == company:
            return item.get("page_content")
    return None
# -----------------------------------------------------------------------------
# 6. FastAPI 엔드포인트 /답변 테스트용 fast api



app = FastAPI()



# 기존 피드백 엔드포인트 (호환)

# @app.post("/ai-feedback", response_model=FeedbackResponse)
# async def ai_feedback(request: FeedbackRequest):
#     if request.company:
#         company_values_text = get_company_values_text(request.company)
#     else:   
#         company_values_text = ""

#     context_docs = ""
#     sources = []

#     # 표준 질문일 경우 question_id로 벡터스토어에서 도큐먼트 검색
#     if request.standard_question == "y" and request.question_id:
#         # question_templates feature에서 question_id 일치하는 도큐먼트 추출
#         all_docs = vectorstore.docstore._dict.values()
#         doc = next((d for d in all_docs if d.metadata.get("feature") == "question_templates" and d.metadata.get("question_id") == request.question_id), None)
#         if doc:
#             context_docs = doc.page_content
#             sources = [request.question_id]
#         else:
#             print(f"question_id {request.question_id}에 해당하는 도큐먼트가 없습니다.")

#     # 표준 질문이 아니면 기존 RAG 검색
#     if not context_docs:
#         try:
#             context_docs, sources = await get_rag_context(
#                 request.job_group,
#                 request.job,
#                 request.company,
#                 request.question,
#                 request.answer,
#             )
#         except Exception as e:
#             print(" RAG 에러, 컨텍스트 없이 진행:", e)
#             context_docs = ""
#             sources = []

#     if company_values_text:
#         context_docs = company_values_text + "\n\n---\n\n" + context_docs
#         sources.insert(0, f"{request.company}-company-values")

#     raw = call_gpt(
#         job=request.job,
#         company=request.company,
#         question=request.question,
#         answer=request.answer,
#         context_docs=context_docs,
#     )
#     feedback = parse_feedback(raw)
#     feedback.retrieved_sources = sources
#     return feedback


# 새로운 질문 랜덤 추출 엔드포인트
import random

@app.post("/random-questions", response_model=RandomQuestionResponse)
async def random_questions(request: RandomQuestionRequest):
    # 1. 벡터스토어에서 question_templates만 추출
    all_docs = vectorstore.docstore._dict.values()
    question_docs = [doc for doc in all_docs if doc.metadata.get("feature") == "question_templates"]

    # 2. q_list에 해당하는 question_type별로 그룹핑
    groups = []
    for q_type in request.q_list:
        filtered = [doc for doc in question_docs if doc.metadata.get("question_type") == q_type]
        # 3. 랜덤 추출 (중복 없이, 개수 부족하면 모두 반환)
        selected = random.sample(filtered, min(request.count, len(filtered))) if filtered else []
        # 4. dict로 변환 (FastAPI 응답 직렬화)
        questions = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in selected]
        groups.append(RandomQuestionGroup(question_type=q_type, questions=questions))

    return RandomQuestionResponse(groups=groups)



@app.post("/search-documents", response_model=SearchDocumentsResponse)
async def search_documents(request: SearchDocumentsRequest = Body(...)):
    # 1. job_family로 1차 필터링
    all_docs = list(vectorstore.docstore._dict.values())
    filtered_docs = [doc for doc in all_docs if doc.metadata.get('job_family') == request.job_family]
    

    # 2. 질문/답변 feature별 후보군 생성
    question_docs = [doc for doc in filtered_docs if doc.metadata.get('feature') == 'question']
    answer_docs = [doc for doc in filtered_docs if doc.metadata.get('feature') == 'answer']

    # 후보군 내에서 벡터 유사도 기반 top_k 추출
    def similarity_search_in_candidates(query, candidates, k):
        if not candidates:
            return []
        # 후보군의 임베딩 추출
        texts = [doc.page_content for doc in candidates]
        query_emb = embedding.embed_query(query)
        doc_embs = embedding.embed_documents(texts)
        # 코사인 유사도 계산
        import numpy as np
        def cosine_sim(a, b):
            a = np.array(a)
            b = np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        sims = [cosine_sim(query_emb, doc_emb) for doc_emb in doc_embs]
        # 유사도 높은 순으로 k개 인덱스 추출
        top_indices = np.argsort(sims)[::-1][:k]
        return [candidates[i] for i in top_indices]

    top_question_docs = similarity_search_in_candidates(request.question, question_docs, request.top_k)
    top_answer_docs = similarity_search_in_candidates(request.answer, answer_docs, request.top_k)

    # 3. answer_docs의 competency_tags 취합 및 관련 도큐먼트 추가
    competency_tags = set()
    for doc in top_answer_docs:
        tags = doc.metadata.get('competency_tags', [])
        if isinstance(tags, list):
            competency_tags.update(tags)
    competency_docs = [doc for doc in all_docs if doc.metadata.get('competency_id') in competency_tags]

    # 4. question_docs의 question_type 기반 answer_patterns 도큐먼트 추가
    question_types = set(doc.metadata.get('question_type') for doc in top_question_docs)
    answer_pattern_docs = [doc for doc in all_docs if doc.metadata.get('feature') == 'answer_patterns' and doc.metadata.get('question_type') in question_types]

    # FastAPI 직렬화: Document 객체를 dict로 변환
    def doc_to_dict(doc):
        return {"page_content": doc.page_content, "metadata": doc.metadata}

    return SearchDocumentsResponse(
        top_question_docs=[doc_to_dict(doc) for doc in top_question_docs],
        top_answer_docs=[doc_to_dict(doc) for doc in top_answer_docs],
        competency_docs=[doc_to_dict(doc) for doc in competency_docs],
        answer_pattern_docs=[doc_to_dict(doc) for doc in answer_pattern_docs],
    )

@app.post("/structured-feedback")
async def structured_feedback(req: StructuredFeedbackRequest = Body(...)):
    # 1. 기존 검색 로직 (RAG)
    search_res = await search_documents(SearchDocumentsRequest(
        job_family=req.job_family,
        question=req.question,
        answer=req.answer,
        top_k=req.top_k,
    ))

    # 2. 컨텍스트 구성
    ctx_parts = []
    for d in search_res.top_question_docs:
        ctx_parts.append(f"[면접 질문 예시]\n{d['page_content']}")
    for d in search_res.top_answer_docs:
        ctx_parts.append(f"[답변 예시]\n{d['page_content']}")
    for d in search_res.competency_docs:
        name = d.get('metadata', {}).get('competency_name') or d.get('metadata', {}).get('competency_id')
        ctx_parts.append(f"[핵심 역량 설명 - {name}]\n{d['page_content']}")
    for d in search_res.answer_pattern_docs:
        pattern = d.get('metadata', {}).get('structure_name') or d.get('metadata', {}).get('question_type')
        ctx_parts.append(f"[추천 답변 구조 - {pattern}]\n{d['page_content']}")
    
    context_block = "\n\n".join(ctx_parts)

    # ------------------------------------------------------------------
    # 3. 회사 인재상 로직 (핵심 수정 부분)
    # ------------------------------------------------------------------
    company_values_content = None
    
    if req.company:
        logger.info(f"사용자가 회사 입력: '{req.company}'")
        found_values = get_company_values(req.company) # DB 조회
        if found_values:
             company_values_content = f"기업명: {req.company}\n내용: {found_values}"
    
    # 4. 프롬프트 동적 구성 (Python에서 제어)
    
    # 공통 프롬프트 상단
    base_prompt = dedent(f"""
    당신은 전문 면접 코치입니다.
    
    [참고 자료]
    {context_block}

    [사용자 질문]
    {req.question}

    [사용자 답변]
    {req.answer}
    
    [작성 규칙]
    - 반드시 "존댓말(합니다체)"를 사용하세요.
    - Markdown 형식을 엄격히 준수하세요.
    - 문단 사이에는 반드시 빈 줄(\\n\\n)을 넣으세요.
    """)

    # 조건에 따른 "인재상 섹션" 및 "출력 포맷" 분기 처리
    if company_values_content:
        # Case A: 회사 정보가 있는 경우 -> 인재상 내용과 출력 포맷 포함
        dynamic_instruction = dedent(f"""
        [회사 인재상 정보]
        {company_values_content}

        [지시 사항]
        위 [회사 인재상 정보]를 분석하여 답변이 기업 문화에 맞는지 평가에 반영하세요.

        아래 형식으로만 출력하세요:

        ### 입력한 기업 인재상
        (여기에는 위 인재상 정보를 2~3문장으로 요약하여 작성)

        ### 기업 맞춤 조언
        (해당 기업 인재상이 요구하는 방향으로 답변을 보완할 구체적 조언 3~5문장)

        ### 전체 총평
        (전체 총평 5~6줄)

        ### 개선포인트
        - [개선포인트1] (이유와 개선 방법)
        - [개선포인트2]
        - [개선포인트3]

        ### 모범답변 예시
        (서론-본론-결론 구조로 작성된 개선된 답변)
        """)
    else:
        # Case B: 회사 정보가 없는 경우 -> 인재상 관련 언급 금지 및 섹션 제외
        dynamic_instruction = dedent(f"""
        [지시 사항]
        사용자가 회사 정보를 입력하지 않았습니다. 
        따라서 **회사, 인재상, 기업 문화에 대한 내용은 절대로 언급하지 마세요.**
        오직 직무 적합성과 답변의 논리성만 평가하세요.

        아래 형식으로만 출력하세요:

        ### 전체 총평
        (전체 총평 30줄)

        ### 개선포인트
        사용자의 답변에서 개선이 왜 필요하고, 어떻게 개선해야할지에 대해 설명
        - [개선포인트1]
        - [개선포인트2]
        - [개선포인트3]

        ### 모범답변 예시
        (서론-본론-결론 구조로 작성된 개선된 답변)
        """)

    # 최종 프롬프트 합치기
    final_prompt = base_prompt + "\n\n" + dynamic_instruction

    # 5. 모델 호출
    resp = client.chat.completions.create(
        model="gpt-4.1-mini", # 혹은 gpt-4o 등 사용 중인 모델
        messages=[
            {"role": "system", "content": "한국어 면접 코치로서 간결하고 실질적인 피드백을 제공합니다."},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.4,
    )

    return {"markdown": resp.choices[0].message.content}