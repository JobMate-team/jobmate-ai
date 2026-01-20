# src/schemas/gen_question_models.py

from pydantic import BaseModel, Field

# 🚀 사용자 입력 데이터 모델
class InterviewInput(BaseModel):
    """면접 질문 생성을 위한 사용자 입력 정보"""
    job_family: str = Field(..., description="직군 (예: 개발, 마케팅, 디자인)")
    job: str = Field(..., description="직무 (예: 백엔드 개발자, 콘텐츠 마케터)")
    company: str = Field(..., description="지원할 회사 이름 (예: Google, 삼성전자)")

# 📝 질문 쌍(카테고리: 질문) 모델
class Question(BaseModel):
    """단일 면접 질문과 카테고리"""
    category: str = Field(..., description="질문 카테고리 (인성, 기술, 직무, 협업, 가치관)")
    question: str = Field(..., description="생성된 면접 질문")

# 🎉 최종 응답 데이터 모델
class InterviewQuestions(BaseModel):
    """생성된 총 5가지 면접 질문 리스트"""
    questions: list[Question]