import os
import json
from src.core.config import logger, DATA_DIR

COMPANY_VALUES_FILE = "company_values.json"

def load_company_values(path: str = None) -> list:
    """
    company_values.json 파일을 리스트로 읽어 반환.
    """
    if path is None:
        path = os.path.join(DATA_DIR, COMPANY_VALUES_FILE)

    if not os.path.exists(path):
        logger.warning(f"company_values 파일을 찾을 수 없음: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                logger.warning(f"{path}의 형태가 list가 아님. 현재 타입: {type(data)}")
                return []
    except Exception as e:
        logger.exception("company_values.json 로드 중 오류 발생:")
        return []

# 전역 로드 (앱 시작 시 최초 1회)
company_values_data: list = load_company_values()
def get_company_values(company: str) -> str | None:
    # [디버깅 로그] 검색 시도 확인
    print(f"DEBUG: 인재상 검색 요청 - 입력된 회사명: '{company}'")
    
    if not company or not company_values_data:
        print("DEBUG: 회사명이 없거나 데이터가 로드되지 않음.")
        return None

    for item in company_values_data:
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata") or {}
        
        # [중요] DB에 있는 이름과 입력된 이름 비교 로그
        db_name = meta.get("company_name")
        db_id = meta.get("company_id")
        
        if db_name == company or db_id == company:
            print(f"DEBUG: 매칭 성공! ({company})")
            return item.get("page_content")
            
    print(f"DEBUG: 매칭 실패. '{company}'에 해당하는 인재상이 DB에 없음.")
    return None