import random
from fastapi import APIRouter, Body
from src.schemas.feedback import (
    RandomQuestionRequest, RandomQuestionResponse, RandomQuestionGroup,
    SearchDocumentsRequest, SearchDocumentsResponse
)
from src.services.rag_service import init_vectorstore, perform_complex_search
import logging
logger = logging.getLogger("JobMateAI")

router = APIRouter()

import random # 상단에 import 되어 있어야 합니다.

import random 

import random 
@router.post("/random-questions", response_model=RandomQuestionResponse)
async def random_questions(request: RandomQuestionRequest):
    
    # 1. 반환할 고정 카테고리 (question_type) 목록 정의
    FIXED_CATEGORIES = ["tenacity", "job", "behavior", "experience", "tech"]
    
    # 2. 필수값인 job_family 요청값 가져오기
    requested_job_family = request.job_family
    
    vectorstore = init_vectorstore()
    # 주의: 실제 환경에서는 .docstore._dict.values() 대신 검색 API를 사용해야 합니다.
    all_docs = vectorstore.docstore._dict.values() 
    
    # 3. 1차 필터링: feature="question"과 job_family 일치 여부로 문서 필터링 (필수 조건)
    question_docs = [
        doc for doc in all_docs 
        if doc.metadata.get("feature") == "question" and 
           doc.metadata.get("job_family") == requested_job_family
    ]
    
    groups = []
    
    for q_type in FIXED_CATEGORIES: 
        logger.info(f"Processing job_family: {requested_job_family} and q_type: {q_type}")

        # 4. 2차 필터링: question_type으로 문서 필터링
        filtered = [doc for doc in question_docs if doc.metadata.get("question_type") == q_type]

        logger.info(f"Found documents for {requested_job_family}/{q_type}: {len(filtered)}개")
        
        # 5. 해당 카테고리에서 무작위로 '하나(1)'의 문서만 선택
        selection_limit = 1
        
        # 문서 선택
        selected_docs = random.sample(filtered, min(selection_limit, len(filtered))) if filtered else []
        
        questions = []
        
        for doc in selected_docs:
            # 6. 질문 목록(qustion_text)에서 하나의 질문을 무작위로 선택
            question_texts_list = doc.metadata.get("qustion_text", []) 
            
            selected_text = ""
            if question_texts_list and isinstance(question_texts_list, list):
                
                # 💡 1. 빈 문자열("")이 아닌 유효한 질문만 필터링합니다.
                valid_questions = [q for q in question_texts_list if q and q.strip()] 
                
                if valid_questions:
                    # 2. 유효한 질문 목록에서 무작위로 선택합니다.
                    selected_text = random.choice(valid_questions)
                else:
                    # 3. 유효한 질문이 없으면 안전 장치 사용 (page_content)
                    selected_text = doc.page_content or "질문 내용 없음 (데이터 오류)"
            else:
                # 안전 장치: qustion_text가 리스트가 아니거나 없을 경우 page_content 사용
                selected_text = doc.page_content or "질문 내용 없음 (데이터 오류)"
            
            # 7. 최종 질문 객체 생성
            questions.append({
                "page_text": selected_text, 
                "metadata": doc.metadata
            })
            
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