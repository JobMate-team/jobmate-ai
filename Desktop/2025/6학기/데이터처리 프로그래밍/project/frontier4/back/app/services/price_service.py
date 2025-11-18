# app/services/price_service.py

import pandas as pd
from pykrx import stock

def fetch_price_history(code: str, start: str | None = None, end: str | None = None):
    """
    PyKRX 기반 주가 데이터 수집
    - code: "005930" 같은 6자리 종목 코드
    - start, end: "2024-01-01" 형태 문자열 (없으면 전체 기간)
    반환: 컬럼 [date, open, high, low, close, volume] 를 가진 DataFrame
    """

    # 기본 날짜 (없으면 넉넉하게)
    if start is None:
        start = "2000-01-01"
    if end is None:
        end = pd.Timestamp.today().strftime("%Y-%m-%d")

    # PyKRX 형식(YYYYMMDD)으로 변환
    start_str = pd.to_datetime(start).strftime("%Y%m%d")
    end_str = pd.to_datetime(end).strftime("%Y%m%d")

    try:
        # OHLCV 데이터 조회
        df = stock.get_market_ohlcv_by_date(start_str, end_str, code)
    except Exception as e:
        print(f"[ERROR] PyKRX fetch failed for {code}: {e}")
        return pd.DataFrame()

    # 데이터 없으면 빈 DF 반환
    if df is None or df.empty:
        return pd.DataFrame()

    # 인덱스(날짜)를 컬럼으로 빼고, 한글 컬럼명을 영문으로 통일
    df = df.reset_index()

    df.rename(
        columns={
            "날짜": "date",
            "시가": "open",
            "고가": "high",
            "저가": "low",
            "종가": "close",
            "거래량": "volume",
        },
        inplace=True,
    )

    # 날짜 정렬
    df = df.sort_values("date").reset_index(drop=True)

    return df
