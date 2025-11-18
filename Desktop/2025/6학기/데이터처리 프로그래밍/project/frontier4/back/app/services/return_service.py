# app/services/return_service.py

import pandas as pd
from .price_service import fetch_price_history


def build_returns_dataframe(codes: list[str], start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """
    여러 종목의 종가 데이터를 가져와서
    → 날짜를 기준으로 병합
    → 결측치 보정(ffill, bfill)
    → 일간 수익률(pct_change) 계산

    반환: index = date, columns = 종목코드 인 수익률 DataFrame
    """

    dfs: list[pd.DataFrame] = []

    for code in codes:
        price_df = fetch_price_history(code, start, end)

        # 데이터가 없으면 skip
        if price_df is None or price_df.empty:
            print(f"[WARN] No price data for {code}")
            continue

        # date 를 인덱스로, close 를 해당 종목 이름으로
        tmp = (
            price_df[["date", "close"]]
            .copy()
            .set_index("date")
            .rename(columns={"close": code})
        )
        dfs.append(tmp)

    # 아무 종목도 데이터가 없으면 빈 DF 반환
    if not dfs:
        return pd.DataFrame()

    # 날짜 기준 outer join 으로 합치기
    df = pd.concat(dfs, axis=1, join="outer")

    # 날짜 정렬
    df = df.sort_index()

    # 결측치: 앞 값으로 채우고(ffill), 시작 부분은 뒷 값으로(bfill)
    df = df.ffill().bfill()

    # 수익률 계산
    returns = df.pct_change().dropna()

    return returns
