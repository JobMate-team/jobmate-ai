import json
from textwrap import dedent
from src.core.config import client, logger

def generate_structured_feedback_content(
    question: str, 
    answer: str, 
    context_block: str, 
    company_values_content: str = None
) -> str:
    """
    회사 인재상 내용(company_values_content)의 유무에 따라 
    서로 다른 프롬프트(출력 포맷)를 적용하여 GPT 응답을 생성합니다.
    """
    
    # 1. 공통 프롬프트 상단
    base_prompt = dedent(f"""
    당신은 전문 면접 코치입니다.
    
    [참고 자료]
    {context_block}

    [사용자 질문]
    {question}

    [사용자 답변]
    {answer}
    
    [작성 규칙]
    - 반드시 "존댓말(합니다체)"를 사용하세요.
    - Markdown 형식을 엄격히 준수하세요.
    - 문단 사이에는 반드시 빈 줄(\\n\\n)을 넣으세요.
    """)

    # 2. 조건에 따른 "인재상 섹션" 및 "출력 포맷" 분기 처리
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
        (전체적인 사용자의 답변을 평가하여 줄글 형식으로 3자세하게 50줄)

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

    # 3. 최종 프롬프트 합치기
    final_prompt = base_prompt + "\n\n" + dynamic_instruction

    # 4. 모델 호출
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",  # (참고) 실제 사용 가능한 모델명인지 확인 필요 (gpt-4o-mini 등)
        messages=[
            {"role": "system", "content": "한국어 면접 코치로서 간결하고 실질적인 피드백을 제공합니다."},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.4,
    )

    return resp.choices[0].message.content