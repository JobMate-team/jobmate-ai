# (파일 상단에 import requests, os, json, load_dotenv 등은 그대로 둡니다)
# (load_dotenv()도 미리 실행해 둡니다)

def get_naver_news(query_word):
    """
    검색어(query_word)를 받아서 네이버 뉴스 API 결과를 반환하는 함수
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    # (키가 없는 경우 예외 처리)
    if not client_id or not client_secret:
        return {"error": ".env 파일에 API 키가 없습니다."}

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    # (중요) 'query' 파라미터를 고정된 '삼성전자'가 아닌,
    # 함수로 전달받은 'query_word'로 설정합니다.
    params = {
        "query": query_word,
        "display": 5  # 5개만 가져오기
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()  # 성공하면 JSON 데이터 반환
    else:
        # 실패하면 에러 코드 반환
        return {"error": f"API Error: {response.status_code}"}

# --- 함수 테스트 (선택 사항) ---
# if __name__ == "__main__":
#     # '카카오'로 테스트 검색
#     news_data = get_naver_news("카카오")
#     print(json.dumps(news_data, indent=4, ensure_ascii=False))