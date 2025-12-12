import json
from textwrap import dedent
from src.core.config import client, logger

def generate_structured_feedback_content(
    question: str, 
    answer: str, 
    context_block: str, 
    company_values_content: str = None
) -> dict: # <-- 반환 타입을 dict으로 수정
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
    - 문단 사이에는 반드시 빈 줄(\\n\\n)을 넣으세요.
    """)

    # 2. 조건에 따른 "인재상 섹션" 및 "출력 포맷" 분기 처리 (기존 JSON 요청 프롬프트 유지)
    if company_values_content:
        # Case A: 회사 정보가 있는 경우
        dynamic_instruction = dedent(f"""
        [회사 인재상 정보]
        {company_values_content}

        [지시 사항]
        위 [회사 인재상 정보]를 분석하여 답변이 기업 문화에 맞는지 평가에 반영하세요.
        위 지침에 따라 분석한 결과를 **반드시 다음 JSON 스키마 형식으로만 출력**하세요.
    
        [JSON 스키마]
        {{
        "요약된_인재상": "(요약된 인재상 2~3문장)",
        "기업_맞춤_조언": "(구체적 조언 3~5문장)",
        "전체_총평": "(자세한 총평  15문장)",
        "개선포인트": [
            "개선포인트1 (이유와 개선 방법)",
            "개선포인트2",
            "개선포인트3"
        ],
        "모범_답변_예시": "(서론-본론-결론 구조로 작성된 개선된 답변)"
        }}

        (JSON 외의 다른 텍스트는 출력하지 마세요.)
    """)
    else:
        # Case B: 회사 정보가 없는 경우
        # Note: 인재상이 없는 경우에도 동일한 JSON 스키마를 유지하되,
        # "요약된_인재상"과 "기업_맞춤_조언" 필드는 'N/A' 등으로 채우도록 프롬프트를 조정하는 것이 안정적입니다.
        dynamic_instruction = dedent(f"""
        [지시 사항]
        사용자가 회사 정보를 입력하지 않았습니다. 
        따라서 **회사, 인재상, 기업 문화에 대한 내용은 절대로 언급하지 마세요.**
        오직 직무 적합성과 답변의 논리성만 평가하세요.
        위 지침에 따라 분석한 결과를 **반드시 다음 JSON 스키마 형식으로만 출력**하세요.
    
        "전체_총평": "(자세한 총평 20문장)",
        "개선포인트": [
            "개선포인트1 (이유와 개선 방법)",
            "개선포인트2",
            "개선포인트3"
        ],
        "모범_답변_예시": "(서론-본론-결론 구조로 작성된 개선된 답변)"
        }}

        (JSON 외의 다른 텍스트는 출력하지 마세요.)
    """)

    # 3. 최종 프롬프트 합치기
    final_prompt = base_prompt + "\n\n" + dynamic_instruction

    # 4. 모델 호출 및 JSON 모드 활성화
    try:
        resp = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "한국어 면접 코치로서 간결하고 실질적인 피드백을 제공합니다."},
                {"role": "user", "content": final_prompt},
            ],
            temperature=0.4,
            # === 핵심 변경: JSON 모드 활성화 ===
            response_format={"type": "json_object"}, 
        )
        
        # 5. 응답 문자열을 Python 딕셔너리로 변환하여 반환
        json_string = resp.choices[0].message.content
        return json.loads(json_string)

    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류 발생: {e}, 원본 응답: {resp.choices[0].message.content}")
        # 오류 발생 시 임시 처리 또는 예외 발생
        return {"error": "JSON 파싱 실패", "raw_output": resp.choices[0].message.content}
    except Exception as e:
        logger.error(f"GPT API 호출 오류: {e}")
        return {"error": f"API 호출 실패: {e}"}

# 함수 호출 후, 결과 딕셔너리에서 특정 필드에 접근할 수 있습니다:
# result = generate_structured_feedback_content(...)
# print(result["모범_답변_예시"])