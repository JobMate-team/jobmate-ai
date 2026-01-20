from fastapi import APIRouter, Body
from src.schemas.feedback import StructuredFeedbackRequest
from src.services.rag_service import perform_complex_search
from src.services.utils import get_company_values
from src.services.ai_service import generate_structured_feedback_content
from src.core.config import logger

router = APIRouter()

@router.post("/structured-feedback")
async def structured_feedback(req: StructuredFeedbackRequest = Body(...)):
    # 1. 문서 검색 (RAG 수행)
    search_res = await perform_complex_search(
        job_family=req.job_family,
        question=req.question,
        answer=req.answer,
        top_k=req.top_k,
    )

    # 2. 컨텍스트 구성 (검색 결과를 하나의 문자열로 합침)
    ctx_parts = []
    # (참고) perform_complex_search 결과는 Document 객체 리스트를 담은 dict
    for d in search_res["top_question_docs"]:
        ctx_parts.append(f"[면접 질문 예시]\n{d.page_content}")
    for d in search_res["top_answer_docs"]:
        ctx_parts.append(f"[답변 예시]\n{d.page_content}")
    for d in search_res["competency_docs"]:
        # 메타데이터 안전 접근
        meta = d.metadata if d.metadata else {}
        name = meta.get('competency_name') or meta.get('competency_id') or "역량"
        ctx_parts.append(f"[핵심 역량 설명 - {name}]\n{d.page_content}")
    for d in search_res["answer_pattern_docs"]:
        meta = d.metadata if d.metadata else {}
        pattern = meta.get('structure_name') or meta.get('question_type') or "구조"
        ctx_parts.append(f"[추천 답변 구조 - {pattern}]\n{d.page_content}")
    
    context_block = "\n\n".join(ctx_parts)

    # 3. 회사 인재상 조회 (원래 main.py 로직과 동일)
    company_values_content = None
    
    if req.company:
        logger.info(f"사용자가 회사 입력: '{req.company}'")
        found_values = get_company_values(req.company) # DB/JSON 조회
        if found_values:
             company_values_content = f"기업명: {req.company}\n내용: {found_values}"
    
    # 4. AI 서비스 호출 (프롬프트 구성 및 GPT 호출 위임)
    # 여기서 company_values_content가 None이면 ai_service 내부에서 
    # 자동으로 'Case B' 프롬프트를 타게 됩니다.
    markdown_response = generate_structured_feedback_content(
        question=req.question,
        answer=req.answer,
        context_block=context_block,
        company_values_content=company_values_content
    )

    return {"markdown": markdown_response}