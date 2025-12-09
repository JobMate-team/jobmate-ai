import random
from fastapi import APIRouter, Body
from src.schemas.feedback import (
    RandomQuestionRequest, RandomQuestionResponse, RandomQuestionGroup,
    SearchDocumentsRequest, SearchDocumentsResponse
)
from src.services.rag_service import init_vectorstore, perform_complex_search

router = APIRouter()

@router.post("/random-questions", response_model=RandomQuestionResponse)
async def random_questions(request: RandomQuestionRequest):
    vectorstore = init_vectorstore()
    all_docs = vectorstore.docstore._dict.values()
    question_docs = [doc for doc in all_docs if doc.metadata.get("feature") == "question_templates"]

    groups = []
    for q_type in request.q_list:
        filtered = [doc for doc in question_docs if doc.metadata.get("question_type") == q_type]
        selected = random.sample(filtered, min(request.count, len(filtered))) if filtered else []
        questions = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in selected]
        groups.append(RandomQuestionGroup(question_type=q_type, questions=questions))

    return RandomQuestionResponse(groups=groups)

@router.post("/search-documents", response_model=SearchDocumentsResponse)
async def search_documents(request: SearchDocumentsRequest = Body(...)):
    # 비즈니스 로직은 Service 계층으로 위임
    result = await perform_complex_search(
        job_family=request.job_family,
        question=request.question,
        answer=request.answer,
        top_k=request.top_k
    )
    
    # Document 객체를 dict로 변환 (FastAPI 응답용)
    def doc_to_dict(doc):
        return {"page_content": doc.page_content, "metadata": doc.metadata}

    return SearchDocumentsResponse(
        top_question_docs=[doc_to_dict(d) for d in result["top_question_docs"]],
        top_answer_docs=[doc_to_dict(d) for d in result["top_answer_docs"]],
        competency_docs=[doc_to_dict(d) for d in result["competency_docs"]],
        answer_pattern_docs=[doc_to_dict(d) for d in result["answer_pattern_docs"]],
    )