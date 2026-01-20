# src/routers/interview.py

from fastapi import APIRouter, Depends, HTTPException
from src.schemas.gen_question_models import InterviewInput, InterviewQuestions 
from src.services.gen_service import generate_questions 

# 🚀 라우터 인스턴스 생성
router = APIRouter(
    prefix="/interview", # 이 라우터의 모든 엔드포인트는 /interview 로 시작합니다.
    tags=["Interview Question Generator"],
)

# 🌐 POST 엔드포인트 정의
@router.post(
    "/generate", 
    response_model=InterviewQuestions,
    summary="직무 기반 면접 질문 5가지 생성"
)
async def generate_interview_questions_endpoint(input_data: InterviewInput):
    """
    사용자 입력(직군, 직무, 회사)을 받아 5가지 카테고리의 질문을 생성합니다.
    """
    try:
        # ⚙️ 서비스 로직 호출
        questions = generate_questions(input_data)
        
        # 🎁 응답 모델에 맞게 데이터 포장
        return InterviewQuestions(questions=questions)
    
    except Exception as e:
        # ⚠️ 예상치 못한 에러 발생 시 500 에러 처리
        raise HTTPException(status_code=500, detail=f"질문 생성 중 오류 발생: {str(e)}")