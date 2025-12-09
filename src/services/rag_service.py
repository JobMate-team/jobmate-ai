import os
import json
import numpy as np
from textwrap import dedent
from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.core.config import embedding, DATA_DIR, FAISS_INDEX_PATH, logger

# 전역 VectorStore 변수
vectorstore = None

def build_faiss_from_json(folder_path: str = DATA_DIR,
                          index_path: str = FAISS_INDEX_PATH) -> None:
    """JSON 파일들을 읽어 FAISS 인덱스 생성 및 저장"""
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
            print(f"파일을 찾을 수 없음: {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                docs.append(
                    Document(
                        page_content=item["page_content"],
                        metadata=item.get("metadata", {}),
                    )
                )

    if not docs:
        raise ValueError("임베딩에 사용할 문서가 없습니다. JSON 파일을 확인하세요.")

    global vectorstore
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(index_path)
    print("FAISS 벡터 DB 생성 완료")

def load_vectorstore(index_path: str = FAISS_INDEX_PATH) -> FAISS:
    """FAISS 인덱스 로드 (없으면 생성)"""
    global vectorstore
    if not os.path.exists(index_path):
        build_faiss_from_json(index_path=index_path)
    
    vectorstore = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
    print("FAISS 벡터 DB 로드 완료")
    return vectorstore

# 초기화 함수 (Main에서 호출)
def init_vectorstore():
    global vectorstore
    if vectorstore is None:
        load_vectorstore()
    return vectorstore

# --- 검색 로직 ---

def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def similarity_search_in_candidates(query, candidates, k):
    if not candidates:
        return []
    texts = [doc.page_content for doc in candidates]
    query_emb = embedding.embed_query(query)
    doc_embs = embedding.embed_documents(texts)
    
    sims = [cosine_sim(query_emb, doc_emb) for doc_emb in doc_embs]
    top_indices = np.argsort(sims)[::-1][:k]
    return [candidates[i] for i in top_indices]

async def perform_complex_search(job_family: str, question: str, answer: str, top_k: int):
    """search-documents 엔드포인트의 핵심 로직"""
    if vectorstore is None:
        init_vectorstore()
        
    all_docs = list(vectorstore.docstore._dict.values())
    
    # 1. job_family 필터링
    filtered_docs = [doc for doc in all_docs if doc.metadata.get('job_family') == job_family]

    # 2. 후보군 생성
    question_docs_candidates = [doc for doc in filtered_docs if doc.metadata.get('feature') == 'question']
    answer_docs_candidates = [doc for doc in filtered_docs if doc.metadata.get('feature') == 'answer']

    # 3. 유사도 검색
    top_question_docs = similarity_search_in_candidates(question, question_docs_candidates, top_k)
    top_answer_docs = similarity_search_in_candidates(answer, answer_docs_candidates, top_k)

    # 4. 관련 문서(역량, 답변 패턴) 추가
    competency_tags = set()
    for doc in top_answer_docs:
        tags = doc.metadata.get('competency_tags', [])
        if isinstance(tags, list):
            competency_tags.update(tags)
    
    competency_docs = [doc for doc in all_docs if doc.metadata.get('competency_id') in competency_tags]

    question_types = set(doc.metadata.get('question_type') for doc in top_question_docs)
    answer_pattern_docs = [doc for doc in all_docs if doc.metadata.get('feature') == 'answer_patterns' and doc.metadata.get('question_type') in question_types]

    return {
        "top_question_docs": top_question_docs,
        "top_answer_docs": top_answer_docs,
        "competency_docs": competency_docs,
        "answer_pattern_docs": answer_pattern_docs
    }

async def get_rag_context(job_group: str, job: str, company: str, question: str, answer: str, k: int = 4) -> Tuple[str, List[str]]:
    """(Legacy) 기존 피드백 요청용 컨텍스트 검색"""
    if vectorstore is None:
        init_vectorstore()

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
    context_texts = []
    sources = []

    for doc in docs:
        context_texts.append(doc.page_content)
        meta = doc.metadata or {}
        source = (
            meta.get("source") or meta.get("question_id") or meta.get("pattern_id") 
            or meta.get("competency_id") or meta.get("id") or ""
        )
        sources.append(str(source))

    context = "\n\n---\n\n".join(context_texts)
    return context, sources