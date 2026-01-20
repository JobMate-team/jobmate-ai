# src/services/interview_generator.py

from src.schemas.gen_question_models import InterviewInput, Question
from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def extract_json(text: str) -> str:
    """
    GPT가 ```json ... ``` 형태로 반환했을 경우 코드블록 제거.
    코드블록이 없으면 원본 그대로 반환.
    """
    if "```" not in text:
        return text.strip()

    start = text.find("```")
    end = text.rfind("```")

    if start != -1 and end != -1 and end > start:
        # ```json 또는 ``` 제거
        block = text[start+3:end].strip()
        if block.startswith("json"):
            block = block[4:].strip()
        return block

    return text.strip()

def generate_questions(input_data: InterviewInput) -> list[Question]:

    category = input_data.job_family
    role = input_data.job
    company = input_data.company
    
    # 1) 프롬프트 작성
    prompt = f"""
    당신은 실제 기업 인사팀의 면접관입니다.
    지원자의 역량, 사고과정, 직무 적합성을 깊이 파악하기 위해 
    실전 면접에서 사용할 질문을 설계하는 역할을 맡고 있습니다. 

    아래 정보를 기반으로 {company}에 지원하는 {role} 지원자에게 
    면접에서 사용할 심층 질문을 창의적이고 논리적으로 생성하세요.

    ### 입력 정보
    - 회사: {company}
    - 직무(role): {role}
    - 질문 개수: 5개
    - 질문 유형 카테고리: 
        - Tenacity (인성)
        - Tech (기술)
        - Job (직무)
        - Experience (경험)
        - Behavior (가치관)

    ### 생성 규칙
    1) 각 질문은 위 카테고리 중 하나를 반드시 선택합니다.
    2) 질문은 구체적이고 실무적이어야 합니다.
    3) 회사/직무 맥락을 자연스럽게 반영하세요.
    4) 모든 질문은 서로 다른 관점을 가져야 합니다.
    5) 과하게 포멀하지 않고 실전 면접 느낌으로 만드세요.


    ### 출력 형식(JSON)
    [
      {{
        "category": "...",
        "question": "..."
      }},
      ...
    ]
    """
    
    # 2) GPT API 호출
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role":"user", "content": prompt}]
    )
    
    raw_output = response.choices[0].message.content.strip()

    clean_json_str = extract_json(raw_output)

    try:
        parsed = json.loads(clean_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"❌ GPT JSON 파싱 실패\n원본:\n{raw_output}\n\n정제 후:\n{clean_json_str}"
        )


    # 4) Question 객체로 변환
    questions = [Question(category=q["category"], question=q["question"]) for q in parsed]

    return questions
