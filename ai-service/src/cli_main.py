### cli_main.py
import os
import json
import re
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from openai import OpenAI

# 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. 먼저 환경 변수를 설정하세요.")

embedding = OpenAIEmbeddings(api_key=api_key)
client = OpenAI(api_key=api_key)

# 1. FAISS DB 생성 함수
def build_faiss_from_json(folder_path="./embedding"):
    docs = []
    for filename in ["question_templates.json", "answer_patterns.json", "competency_rubrics.json", "model_answers.json"]:
        filepath = os.path.join(folder_path, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ 파일을 찾을 수 없음: {filepath}")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                docs.append(Document(page_content=item["page_content"], metadata=item["metadata"]))

    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local("faiss_index")
    print("✅ FAISS 벡터 DB 생성 완료")

# 2. 프롬프트 생성 템플릿
def build_prompt(question, answer, context):
    return f"""
너는 신입 백엔드 개발자의 면접 코치입니다.
답변을 평가할 때는 문제 해결력, 기술 이해도, 전달력을 기준으로 평가하세요.
답변 구조가 STAR에 적합한지, 각 단계가 잘 표현되었는지 유심히 살펴보세요.

[면접 질문]
{question}

[사용자 답변]
{answer}

[문서 컨텍스트 (참고 자료)]
{context}

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
"""

# 3. 응답 파싱 함수
def parse_star_feedback(output):
    star_scores = {}
    pattern = r"(Situation|Task|Action|Result):\s*(\d)/(\d)\s*-\s*(.*)"
    matches = re.findall(pattern, output)
    for section, score, total, comment in matches:
        star_scores[section] = {
            "score": int(score),
            "out_of": int(total),
            "comment": comment.strip()
        }
    return star_scores

# 4. 사용자 입력 후 RAG 기반 응답 생성
def run_rag_interaction():
    db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)

    print("[면접 질문 입력]")
    question = input("Q: ")
    print("[사용자 답변 입력]")
    answer = input("A: ")

    docs = db.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = build_prompt(question, answer, context)

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "넌 면접 피드백 코치야."},
            {"role": "user", "content": prompt}
        ]
    )

    output = completion.choices[0].message.content
    print("\n📌 전체 응답:\n")
    print(output)

    # STAR 점수 파싱
    star_feedback = parse_star_feedback(output)
    print("\n📊 STAR 구조 평가 결과:")
    for section, data in star_feedback.items():
        print(f"- {section}: {data['score']}/{data['out_of']} - {data['comment']}")

# 실행
def main():
    if not os.path.exists("faiss_index"):
        build_faiss_from_json()
    run_rag_interaction()

if __name__ == "__main__":
    main()
