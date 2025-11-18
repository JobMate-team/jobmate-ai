from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import time, requests
from bs4 import BeautifulSoup   # 네이버 검색 HTML 파싱용

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*"]}})

NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


# -----------------------------------
# 1) 네이버 “주식 검색” 자동 파싱 (이름/코드 둘 다 지원)
# -----------------------------------
def search_naver_stocks(query: str):
    """네이버 금융 검색 결과에서 (종목코드, 종목명) 추출"""
    url = f"https://finance.naver.com/search/searchList.naver?query={query}"
    r = requests.get(url, headers=NAVER_HEADERS, timeout=5)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for row in soup.select("table.tbl_search tbody tr"):
        link = row.select_one("a")
        if not link:
            continue

        name = link.text.strip()                  # 종목명
        href = link.get("href")                   # "/item/main.nhn?code=005930"
        if "code=" not in href:
            continue

        code = href.split("code=")[1][:6]         # 종목코드
        items.append({"code": code, "name": name})

        if len(items) >= 20:
            break

    return items


# -----------------------------------
# 2) 네이버 요약 JSON (현재가/등락률)
# -----------------------------------
def fetch_naver_summary(code: str):
    url = f"https://api.finance.naver.com/service/itemSummary.nhn?itemcode={code}"
    r = requests.get(url, headers=NAVER_HEADERS, timeout=5)
    r.raise_for_status()
    j = r.json()

    now = j.get("now")
    rate = j.get("rate", 0.0)
    name = j.get("nm", f"종목({code})")
    return name, now, rate


# -----------------------------------
# 3) 메모리 저장
# -----------------------------------
collected = {}   # code → dict


# -----------------------------------
# 4) 검색 엔드포인트
# -----------------------------------
@app.get("/stocks")
def list_or_search():
    q = (request.args.get("q") or "").strip()

    # 검색어 있으면 네이버 실시간 검색 수행
    if q:
        try:
            results = search_naver_stocks(q)
            return jsonify(results)
        except Exception as e:
            print("[검색 오류]", e)
            return jsonify([])

    # 검색어 없으면 수집된 종목 반환
    return jsonify(list(collected.values()))


# -----------------------------------
# 5) 종목 추가 (네이버에서 실시간 시세)
# -----------------------------------
@app.post("/stocks")
def add_stock():
    data = request.get_json(silent=True) or {}

    code = (data.get("code") or "").strip()
    name = (data.get("name") or "").strip()

    if not code:
        abort(400, "code required")

    # 네이버 요약에서 가격/등락률 가져오기
    try:
        name2, now, rate = fetch_naver_summary(code)
        if not name:
            name = name2
    except:
        abort(400, "invalid stock code")

    item = {
        "code": code,
        "name": name,
        "price": f"{now:,}원" if now else "-",
        "change": f"{'+' if rate >= 0 else ''}{rate}%",
        "ts": int(time.time()),
    }

    collected[code] = item
    return item, 201


# -----------------------------------
# 6) 종목 삭제
# -----------------------------------
@app.delete("/stocks/<code>")
def delete_stock(code):
    if code in collected:
        del collected[code]
        return "", 204
    abort(404)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
