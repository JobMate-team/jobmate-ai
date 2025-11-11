import pandas as pd
import numpy as np
import quantstats as qs


def cal_nav(W: pd.DataFrame, st_date: str, ed_date: str, init_value: int, bp: float, ret_df: pd.DataFrame):
    """
    W: portfolio weights
    st_date: backtest start date
    ed_date: backtest end date
    init_value: Backtest start value which is pre-defined in config file
    bp: Trading cost for portfolio rebalancing
    ret_df: Portfolio Holdings return dataframe

    Reference.
    - 장마감 직전에 팔면서 같이 산다고 가정
    - EMP SITE 에서는 M to M으로 거래비용 계산
    - Madirid 에서는 D to D로 거래비용 계산
    """
    # Slice to backtest periods
    if pd.to_datetime(st_date) < W.index[0]:
        print("시뮬레이션 시작 시점이 포트폴리오 비중 시작일보다 작습니다.")
        raise
    
    
    W = W.loc[st_date:ed_date]
    ret_df = ret_df.loc[st_date:ed_date]

    daily_dates = ret_df.index
    rebal_dates = W.index

    # Make padding dataframe
    Vh = pd.DataFrame(index=daily_dates, columns=W.columns)
    Pw = pd.DataFrame(index=daily_dates, columns=W.columns)
    
    for i in range(len(daily_dates)):
        t = daily_dates[i]
        
        if i == 0:
            Vh.iloc[i] = W.iloc[i] * init_value            
            continue

        Vh.iloc[i] = Vh.iloc[i-1] * (1 + ret_df.loc[t])

        if t in rebal_dates:
            try:
                cur_holdings = Vh.iloc[i]
                new_holdings = W.loc[t] * cur_holdings.sum()

                trade_val = np.abs(new_holdings - cur_holdings).sum()
                trade_fee = trade_val * bp

                Vh.loc[t] = W.loc[t]*(cur_holdings.sum()-trade_fee)
            except Exception as e:
                print(t)
                print(e)
                return Vh.sum(axis=1), Pw, Vh
        
        try:
            Pw.iloc[i] = Vh.iloc[i]/Vh.iloc[i].sum()
        except:
            print(Vh.iloc[i].sum())
            print(t)
            raise           

    nav = Vh.sum(axis=1)

    return nav, Pw, Vh


def get_summary_pf(concat_nav: pd.DataFrame) -> pd.DataFrame:
    # Performance
    sharpe = qs.stats.sharpe(concat_nav.pct_change().fillna(0))
    cum_ret = (concat_nav.iloc[-1] / concat_nav.iloc[0]) - 1 
    vol = qs.stats.volatility(concat_nav.pct_change().fillna(0))
    cagr = qs.stats.cagr(concat_nav.pct_change().fillna(0))
    mdd = qs.stats.max_drawdown(concat_nav.pct_change().fillna(0))
           
    skew = qs.stats.skew(concat_nav.pct_change().fillna(0))
    kurtosis = qs.stats.kurtosis(concat_nav.pct_change().fillna(0))
    

    pf_ms = pd.concat([cum_ret, sharpe, vol, cagr, mdd, skew, kurtosis], axis=1)
    pf_ms.columns = ['Cumulative Return', 'Sharpe ratio', 'Annualized volatility', 'CAGR', 'Maximum Drawdown', 'Return skewness', 'Return kurtosis']

    pf_ms = pf_ms.apply(lambda x: np.round(x, 3))

    return pf_ms


def pr_reverse(ct: pd.DataFrame, ret_idx: pd.DataFrame, index_mapper: dict)->pd.DataFrame():
    """
    ct: 가격 데이터
    ret_idx: 인덱스 수익률 데이터
    e.g. mapper = {'2803HK': "CSI",
                    '2817HK': "CHINA TREASURY",
                    'GLD': "GOLD"}
    index_mapper: 인덱스와 수익률 자산 매핑 데이터
    e.g. idx_mapper = {'CSI':"CSIR2927",
                       'CHINA TREASURY':"I32561US"}
    """
    for col in ct.columns:
        print(col)
        ct = ct.loc[ret_idx.index[0]:]     
        ct = ct.reindex(ret_idx.index)

        if col not in idx_mapper.keys():
            continue

        if len(ct[col][ct[col].isna()]) == 0:
            continue

        if ct[col][ct[col].isna()].index[-1] < ret_idx[idx_mapper[col]][~ret_idx[idx_mapper[col]].isna()].index[0]:
            continue

        day_list = ret_idx.loc[:ct[col].dropna().index[0]].sort_index(ascending=False).index      

        for i in range(1, len(day_list)):        
            dt = day_list[i-1]

            insert_dt = day_list[i]

            value = ct.loc[dt, col] / (ret_idx.loc[dt, idx_mapper[col]] + 1)

            ct[col].loc[insert_dt] = value
    return ct 


def get_corr_ts(base_asset: str, targets: list, periods:int, returns:pd.DataFrame):
    import scipy.stats as stats

    overall_corr = []
    for i in targets:
        corr_ = []
        for idx in range(periods, len(returns), 1):
            ext = returns.iloc[idx-periods:idx]
            corr_.append(stats.pearsonr(ext.loc[:,base_asset], ext.loc[:,i])[0])
        overall_corr.append(corr_)
    return overall_corr