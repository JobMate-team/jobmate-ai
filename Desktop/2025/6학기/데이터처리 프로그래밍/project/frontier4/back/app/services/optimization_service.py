# app/services/optimization_service.py
import numpy as np
import pandas as pd
from scipy.optimize import minimize

def compute_efficient_frontier(returns: pd.DataFrame, n_points: int = 40):
    """
    Markowitz Efficient Frontier 계산 함수
    returns : 일간 수익률 DF (columns = 종목)
    """
    returns = returns.dropna()
    X = returns.values
    n = X.shape[1]

    mu_daily = returns.mean().values
    mu = mu_daily * 252
    cov = returns.cov().values * 252

    # 최소분산 포트폴리오 찾기
    def min_variance():
        w0 = np.ones(n) / n
        bounds = [(0, 1)] * n
        cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        
        def obj(w):
            return w @ cov @ w
        
        res = minimize(obj, w0, bounds=bounds, constraints=cons)
        return res.x

    w_min = min_variance()
    r_min = w_min @ mu
    r_max = mu.max()

    targets = np.linspace(r_min, r_max, n_points)

    risks = []
    returns_ = []
    weights_list = []

    # 타겟 수익률 기반 프론티어
    for R_target in targets:
        def obj(w):
            return w @ cov @ w
        
        cons = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w: w @ mu - R_target},
        ]
        bounds = [(0, 1)] * n
        w0 = np.ones(n) / n

        res = minimize(obj, w0, bounds=bounds, constraints=cons)

        if res.success:
            w = res.x
            vol = np.sqrt(w @ cov @ w)
            risks.append(float(vol))
            returns_.append(float(w @ mu))
            weights_list.append(w.tolist())

    return risks, returns_, weights_list

def optimize_for_risk(returns_df, risk_target, annual_freq=252):
    """
    risk_target : 0~1 (프론트 슬라이더 값)
    risk_target * achievable_range → target_vol
    """
    import numpy as np
    from scipy.optimize import minimize

    X = returns_df.values
    n = X.shape[1]

    mu = np.mean(X, axis=0) * annual_freq
    cov = np.cov(X, rowvar=False) * annual_freq

    w0 = np.ones(n) / n

    vols = np.sqrt(np.clip(np.diag(cov), 1e-12, None))
    min_risk = float(vols.min())
    max_risk = float(vols.max())

    target_vol = min_risk + risk_target * (max_risk - min_risk)

    def objective(w):
        ret = w @ mu
        vol = np.sqrt(w @ cov @ w)
        return -ret + 500 * (vol - target_vol) ** 2

    cons = ({'type':'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0,1)] * n

    res = minimize(objective, w0, bounds=bounds, constraints=cons)

    w = res.x
    vol = float(np.sqrt(w @ cov @ w))
    ret = float(w @ mu)

    return w.tolist(), vol, ret
