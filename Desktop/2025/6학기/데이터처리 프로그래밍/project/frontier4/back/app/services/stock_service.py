# app/services/stock_service.py

import re
import requests
from bs4 import BeautifulSoup

# 네이버 쪽에서 봇으로 오해하지 않게 UA만 넣어줌
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    )
}

# ---------------------------------------------------------
# 1. 종목명 → 종목코드 (finance.naver.com/search/searchList.naver HTML만 사용)
# ---------------------------------------------------------
def get_stock_code_from_name(name: str) -> str | None:
    """
    네이버 금융 검색 페이지 HTML에서
    'item/main...?code=XXXXXX' 형태의 첫 번째 코드를 긁어온다.
    (HTML 구조가 바뀌어도 href 안에 code=만 있으면 동작하도록 최대한 단순하게)
    """
    name = name.strip()
    if not name:
        return None

    url = "https://finance.naver.com/search/searchList.naver"
    params = {"query": name}

    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=5)
        res.raise_for_status()
    except Exception:
        # 검색 페이지 자체 호출 실패
        return None

    # 인코딩은 requests가 대부분 알아서 잡지만,
    # 혹시 이상하면 추정값(apparent_encoding)으로 한 번 더 맞춰줌
    if not res.encoding or res.encoding.lower() == "iso-8859-1":
        res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")

    # HTML 안의 모든 <a href="...">를 훑으면서,
    # href에 'item/main' + 'code=6자리' 가 있는 첫 번째 것을 사용
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "item/main" in href and "code=" in href:
            m = re.search(r"code=(\d{6})", href)
            if m:
                return m.group(1)

    # 아무 코드도 못 찾음
    return None


# ---------------------------------------------------------
# 2. 종목코드 → 상세 정보 (finance.naver.com/item/main.nhn HTML)
# ---------------------------------------------------------
def fetch_stock_detail_from_naver(code: str) -> dict | None:
    """
    코드(6자리)로 네이버 금융 종목 페이지를 크롤링해서
    종목명 / 현재가 / 전일대비 / 등락률을 가져온다.
    """
    code = code.strip()
    if not code:
        return None

    url = f"https://finance.naver.com/item/main.nhn?code={code}"

    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        res.raise_for_status()
    except Exception:
        return None

    # 인코딩 보정
    if not res.encoding or res.encoding.lower() == "iso-8859-1":
        res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")

    # 종목명
    name_tag = soup.select_one("div.wrap_company h2 a")
    name = name_tag.text.strip() if name_tag else None

    # 현재가
    price_tag = soup.select_one("p.no_today span.blind")
    price_text = price_tag.text.strip() if price_tag else None

    # 전일대비 / 등락률
    exday_spans = soup.select("p.no_exday span.blind")
    change_text = exday_spans[0].text.strip() if len(exday_spans) >= 1 else None
    change_rate_text = exday_spans[1].text.strip() if len(exday_spans) >= 2 else None

    if change_rate_text and not change_rate_text.endswith("%"):
        change_rate_text += "%"

    if not price_text:
        # 가격 자체가 안 잡히면 실패로 간주
        return None

    return {
        "code": code,
        "name": name,
        "price": price_text,
        "change": change_text,
        "changeRate": change_rate_text,
    }


# ---------------------------------------------------------
# 3. 라우트에서 쓰는 메인 함수
#    - 6자리 숫자면 그대로 코드 사용
#    - 아니면 HTML 검색으로 코드 찾고 → 상세 조회
# ---------------------------------------------------------
def get_stock_info(keyword: str) -> dict | None:
    if not keyword:
        return None

    keyword = keyword.strip()

    # 1) 6자리 숫자면 바로 코드로 사용 (이미 잘 되던 부분)
    if re.fullmatch(r"\d{6}", keyword):
        code = keyword
    else:
        # 2) 종목명인 경우 → 검색 HTML에서 코드 찾기
        code = get_stock_code_from_name(keyword)
        if not code:
            return None

    # 3) 코드로 상세 정보 조회
    return fetch_stock_detail_from_naver(code)
