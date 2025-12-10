from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- 기존 호환 모델 ---
class FeedbackRequest(BaseModel):
    job_group: str
    job: str
    company: str
    question: str
    answer: str
    standard_question: str = "n"
    question_id: str = None

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

# --- 랜덤 질문 추출 모델 ---
class RandomQuestionRequest(BaseModel):
    job_family: str
    q_list: list[str]
    count: int

class RandomQuestionGroup(BaseModel):
    question_type: str
    questions: list[dict]

class RandomQuestionResponse(BaseModel):
    groups: list[RandomQuestionGroup]

# --- 문서 검색 모델 ---
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

# --- 구조화된 피드백 모델 ---
class StructuredFeedbackRequest(BaseModel):
    company: str | None = None
    job_family: str
    question: str
    answer: str
    top_k: int = 3