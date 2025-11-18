import pandas as pd
import numpy as np

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from scipy.optimize import minimize


# ---------- Helper ----------
def _weights_dict_to_array(wdict, columns):
    return np.array([wdict.get(col, 0.0) for col in columns])


def clean_weights_array(arr, cutoff=1e-8, rounding=6):
    a = np.array(arr).copy()
    a[np.abs(a) < cutoff] = 0.0
    if rounding is not None:
        a = np.round(a, rounding)
    s = a.sum()
    if s != 0:
        a = a / s
    else:
        a = np.ones_like(a) / len(a)
    return a


def _clean_returns_df(returns_df: pd.DataFrame) -> pd.DataFrame:
    df = returns_df.replace([np.inf, -np.inf], np.nan).dropna(how="any")
    return df


# ---------- 공통: 포트폴리오 성과 계산 ----------
def _compute_portfolio_stats(returns: pd.DataFrame, weights, annual_freq: int = 252):
    """
    returns: (T x N) 수익률
    weights: 길이 N 벡터
    """
    w = np.array(weights, dtype=float)

    if returns.empty:
        return float("nan"), float("nan")

    port_ret = returns.values @ w

    mean_daily = np.nanmean(port_ret)
    std_daily = np.nanstd(port_ret, ddof=1)

    expected_return = float(mean_daily * annual_freq)
    risk = float(std_daily * np.sqrt(annual_freq))

    return risk, expected_return


def _get_recent_window(returns: pd.DataFrame, last_index, lookback: int | None):
    """
    마지막 rebalancing 시점(last_index)까지의 구간 중 최근 lookback 기간만 잘라서 리턴
    """
    try:
        sub = returns.loc[:last_index]
    except Exception:
        sub = returns

    if lookback is not None and len(sub) > lookback:
        sub = sub.iloc[-lookback:]

    return sub


# ---------- utility: build rebalancing indices ----------
def _build_rebal_index(
    returns_index: pd.DatetimeIndex, lookback_periods: int, rebal_periods: str
):
    if len(returns_index) <= lookback_periods:
        return returns_index

    start = returns_index[lookback_periods]
    end = returns_index[-1]

    cand = pd.date_range(start, end, freq=rebal_periods)
    rebal_indice = returns_index[returns_index.get_indexer(cand, method="ffill")]

    rebal_indice = rebal_indice.unique()
    rebal_indice = rebal_indice[rebal_indice.notnull()]
    return rebal_indice


# ---------- Maximize Diversification ----------
def MaximizeDiversification(
    rebal_periods: str,
    returns: pd.DataFrame,
    lookback_periods: int,
    bnd=None,
    long_only=True,
    frequency: int = 252,
):
    returns = _clean_returns_df(returns)
    cols = returns.columns

    def calc_diversification_ratio(w, V):
        w = np.array(w)
        w_vol = np.dot(np.sqrt(np.diag(V)), w.T)
        port_vol = np.sqrt(np.dot(w.T, np.dot(V, w)))
        diversification_ratio = w_vol / port_vol if port_vol > 0 else 0.0
        return -diversification_ratio

    def total_weight_constraint(x):
        return x.sum() - 1.0

    def get_weights(w0, V, bnd, long_only):
        cons = ({"type": "eq", "fun": total_weight_constraint},)
        if long_only and bnd is None:
            bnd = [(0, 1)] * len(w0)
        try:
            res = minimize(
                calc_diversification_ratio,
                w0,
                bounds=bnd,
                args=(V,),
                method="SLSQP",
                constraints=cons,
            )
            W = clean_weights_array(res.x)
        except Exception:
            W = np.ones(len(w0)) / len(w0)
        return W

    w0 = np.array([1 / len(cols)] * len(cols))
    rebal_indice = _build_rebal_index(returns.index, lookback_periods, rebal_periods)

    Pw_list = []
    for idx in rebal_indice:
        ext_returns = returns.loc[:idx].iloc[-lookback_periods:]
        try:
            V = risk_models.sample_cov(
                ext_returns, returns_data=True, frequency=frequency
            ).values
        except Exception:
            V = ext_returns.cov().values

        W = get_weights(w0, V, bnd, long_only)
        Pw_list.append(W)

    Pw = pd.DataFrame(Pw_list, index=rebal_indice, columns=cols)
    return Pw


# ---------- Mean-Variance Max Sharpe ----------
def MeanVarianceMaxSharpe(
    rebal_periods: str,
    returns: pd.DataFrame,
    lookback_periods: int,
    frequency: int = 252,
):
    returns = _clean_returns_df(returns)
    cols = returns.columns

    rebal_indice = _build_rebal_index(returns.index, lookback_periods, rebal_periods)
    Pw_list = []

    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]

        if ext_df.shape[0] < max(10, len(cols)):
            W = np.ones(len(cols)) / len(cols)
            Pw_list.append(W)
            continue

        try:
            mu = expected_returns.mean_historical_return(
                ext_df, returns_data=True, compounding=True, frequency=frequency
            )
            S = risk_models.sample_cov(ext_df, returns_data=True, frequency=frequency)
            ef = EfficientFrontier(mu, S)
            ef.max_sharpe()
            wdict = ef.clean_weights()
            W = clean_weights_array(_weights_dict_to_array(wdict, cols))
        except Exception:
            W = np.ones(len(cols)) / len(cols)

        Pw_list.append(W)

    Pw = pd.DataFrame(Pw_list, index=rebal_indice, columns=cols)
    return Pw


# ---------- Mean-Variance Min Volatility ----------
def MeanVarianceMinVolatility(
    rebal_periods: str,
    returns: pd.DataFrame,
    lookback_periods: int,
    frequency: int = 252,
):
    returns = _clean_returns_df(returns)
    cols = returns.columns

    rebal_indice = _build_rebal_index(returns.index, lookback_periods, rebal_periods)
    Pw_list = []

    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]

        if ext_df.shape[0] < max(10, len(cols)):
            W = np.ones(len(cols)) / len(cols)
            Pw_list.append(W)
            continue

        try:
            mu = expected_returns.mean_historical_return(
                ext_df, returns_data=True, compounding=True, frequency=frequency
            )
            S = risk_models.sample_cov(ext_df, returns_data=True, frequency=frequency)
            ef = EfficientFrontier(mu, S)
            ef.min_volatility()
            wdict = ef.clean_weights()
            W = clean_weights_array(_weights_dict_to_array(wdict, cols))
        except Exception:
            W = np.ones(len(cols)) / len(cols)

        Pw_list.append(W)

    Pw = pd.DataFrame(Pw_list, index=rebal_indice, columns=cols)
    return Pw


# ---------- Risk Parity ----------
def RP(
    rebal_periods: str,
    returns: pd.DataFrame,
    lookback_periods: int,
    frequency: int = 252,
    cov_type: str = "simple",
):
    from pypfopt.risk_models import exp_cov

    returns = _clean_returns_df(returns)
    cols = returns.columns

    def weight_sum_constraint(x):
        return x.sum() - 1.0

    def get_covmat(rets, cov_type):
        if cov_type == "simple":
            return rets.cov().values
        elif cov_type == "exponential":
            return exp_cov(
                rets, returns_data=True, span=len(rets), frequency=frequency
            ).values
        else:
            return rets.cov().values

    def risk_parity_objective(x, covmat):
        x = np.array(x)
        port_var = float(x.T @ covmat @ x)
        if port_var <= 0:
            return 1e9
        sigma = np.sqrt(port_var)
        mrc = (covmat @ x) / sigma
        rc = x * mrc
        return np.sum((rc - rc.mean()) ** 2)

    rebal_indice = _build_rebal_index(returns.index, lookback_periods, rebal_periods)
    Pw_list = []

    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]

        if ext_df.shape[0] < max(10, len(cols)):
            Pw_list.append(np.ones(len(cols)) / len(cols))
            continue

        covmat = get_covmat(ext_df, cov_type)

        x0 = np.repeat(1 / covmat.shape[1], covmat.shape[1])
        cons = ({"type": "eq", "fun": weight_sum_constraint},)

        try:
            res = minimize(
                fun=risk_parity_objective,
                x0=x0,
                args=(covmat,),
                method="SLSQP",
                constraints=cons,
            )
            if res.success:
                W = clean_weights_array(res.x)
            else:
                W = np.ones(len(cols)) / len(cols)
        except Exception:
            W = np.ones(len(cols)) / len(cols)

        Pw_list.append(W)

    Pw = pd.DataFrame(Pw_list, index=rebal_indice, columns=cols)
    return Pw


# ---------- Friendly wrapper functions ----------
def compute_min_variance(
    returns: pd.DataFrame,
    lookback: int = 60,
    freq: str = "M",
    annual_freq: int = 252,
):
    Pw = MeanVarianceMinVolatility(freq, returns, lookback, frequency=annual_freq)
    last_idx = Pw.index[-1]
    w = Pw.loc[last_idx].values

    window = _get_recent_window(returns, last_idx, lookback)
    risk, exp_ret = _compute_portfolio_stats(window, w, annual_freq)

    return w, risk, exp_ret


def compute_max_sharpe(
    returns: pd.DataFrame,
    lookback: int = 60,
    freq: str = "M",
    annual_freq: int = 252,
):
    Pw = MeanVarianceMaxSharpe(freq, returns, lookback, frequency=annual_freq)
    last_idx = Pw.index[-1]
    w = Pw.loc[last_idx].values

    window = _get_recent_window(returns, last_idx, lookback)
    risk, exp_ret = _compute_portfolio_stats(window, w, annual_freq)

    return w, risk, exp_ret


def compute_risk_parity(df: pd.DataFrame, annual_freq: int = 252):
    """
    리스크 패리티 포트폴리오 계산
    - weights, risk(연간 변동성), expected_return(연간 기대수익률) 반환
    """

    if isinstance(df, pd.Series):
        df = df.to_frame()

    returns = _clean_returns_df(df)
    returns = returns.replace([np.inf, -np.inf], np.nan).dropna(how="any")

    if returns.empty or returns.shape[0] < 5 or returns.shape[1] == 0:
        n = returns.shape[1] if returns.shape[1] > 0 else 0
        if n == 0:
            return np.array([]), float("nan"), float("nan")
        w = np.ones(n) / n
        risk, exp_ret = _compute_portfolio_stats(returns, w, annual_freq)
        return w, risk, exp_ret

    X = returns.values
    n = X.shape[1]

    mu_daily = np.nanmean(X, axis=0)
    mu_daily = np.nan_to_num(mu_daily, nan=0.0, posinf=0.0, neginf=0.0)
    mu = mu_daily * annual_freq

    cov_daily = np.cov(X, rowvar=False)
    cov_daily = np.nan_to_num(cov_daily, nan=0.0, posinf=0.0, neginf=0.0)
    cov_daily = (cov_daily + cov_daily.T) / 2.0
    cov = cov_daily * annual_freq

    if not np.any(cov):
        w = np.ones(n) / n
        risk, exp_ret = _compute_portfolio_stats(returns, w, annual_freq)
        return w, risk, exp_ret

    w0 = np.ones(n) / n

    def risk_contribution(w: np.ndarray, covmat: np.ndarray):
        w = np.asarray(w, dtype=float)
        w = np.clip(w, 0.0, 1.0)
        s = w.sum()
        if s <= 0:
            w = np.ones_like(w) / len(w)
        else:
            w /= s

        port_var = float(w @ covmat @ w)
        if port_var <= 0 or not np.isfinite(port_var):
            return np.zeros_like(w)

        sigma_p = np.sqrt(port_var)
        marginal = covmat @ w
        RC = w * marginal / sigma_p
        RC = np.nan_to_num(RC, nan=0.0, posinf=0.0, neginf=0.0)
        return RC

    def objective(w: np.ndarray, covmat: np.ndarray):
        RC = risk_contribution(w, covmat)
        if not np.all(np.isfinite(RC)):
            return 1e9
        target = RC.mean()
        return float(np.sum((RC - target) ** 2))

    cons = ({"type": "eq", "fun": lambda w: np.sum(np.clip(w, 0.0, 1.0)) - 1.0},)
    bounds = [(0.0, 1.0)] * n

    try:
        res = minimize(
            objective,
            w0,
            args=(cov,),
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 500},
        )

        if (not res.success) or (not np.all(np.isfinite(res.x))):
            w = w0
        else:
            w = res.x
    except Exception:
        w = w0

    w = clean_weights_array(w)

    risk, exp_ret = _compute_portfolio_stats(returns, w, annual_freq)

    return w, risk, exp_ret


def compute_equal_weight(returns: pd.DataFrame):
    cols = returns.columns
    w = np.ones(len(cols)) / len(cols)
    idx = [returns.index[-1]]
    return pd.DataFrame([w], index=idx, columns=cols)


def compute_max_diversification(
    returns: pd.DataFrame,
    lookback: int = 60,
    freq: str = "M",
    annual_freq: int = 252,
):
    Pw = MaximizeDiversification(freq, returns, lookback, frequency=annual_freq)
    last_idx = Pw.index[-1]
    w = Pw.loc[last_idx].values

    window = _get_recent_window(returns, last_idx, lookback)
    risk, exp_ret = _compute_portfolio_stats(window, w, annual_freq)

    return w, risk, exp_ret


# ---------- 🔥 Target Risk (Slider 0~1 → 실제 리스크 범위로 매핑) ----------
def compute_target_risk(
    returns: pd.DataFrame,
    target_ratio: float,
    annual_freq: int = 252,
):
    """
    target_ratio: 0~1 슬라이더 위치
    """

    returns = _clean_returns_df(returns)
    if returns.empty or returns.shape[1] == 0:
        return np.array([]), float("nan"), float("nan")

    X = returns.values
    n = X.shape[1]

    mu_daily = np.nanmean(X, axis=0)
    mu = mu_daily * annual_freq
    cov_daily = np.cov(X, rowvar=False)
    cov = cov_daily * annual_freq

    if not np.all(np.isfinite(cov)):
        cov = np.nan_to_num(cov)

    w0 = np.ones(n) / n

    diag = np.clip(np.diag(cov), 1e-12, None)
    asset_vols = np.sqrt(diag)
    eq_vol = float(np.sqrt(w0 @ cov @ w0))

    min_risk = float(min(asset_vols.min(), eq_vol))
    max_risk = float(asset_vols.max())

    if not np.isfinite(min_risk) or not np.isfinite(max_risk) or max_risk <= 0:
        port_ret = float(mu @ w0)
        port_vol = float(eq_vol)
        return w0, port_vol, port_ret

    if min_risk >= max_risk:
        max_risk = min_risk * 1.5

    tr = float(target_ratio)
    if not np.isfinite(tr):
        tr = 0.5
    tr = max(0.0, min(1.0, tr))

    target_vol = min_risk + tr * (max_risk - min_risk)

    def objective(w, mu, cov, t_vol, lam=1000.0):
        w = np.array(w)
        w = np.clip(w, 0.0, 1.0)
        s = w.sum()
        if s <= 0:
            w = np.ones_like(w) / len(w)
        else:
            w = w / s

        port_ret = float(w @ mu)
        port_var = float(w @ cov @ w)
        if port_var < 0:
            port_var = 0.0
        vol = np.sqrt(port_var)
        return -port_ret + lam * (vol - t_vol) ** 2

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, 1.0)] * n

    try:
        res = minimize(
            objective,
            w0,
            args=(mu, cov, target_vol),
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 500},
        )

        if not res.success:
            w = w0
        else:
            w = res.x

    except Exception:
        w = w0

    w = clean_weights_array(w)

    port_var = float(w @ cov @ w)
    if port_var < 0:
        port_var = 0.0
    vol = float(np.sqrt(port_var))
    ret = float(w @ mu)

    return w, vol, ret


def compute_efficient_frontier(df, n_points=40):
    """
    효율적 프론티어 계산
    df: 수익률 DataFrame
    n_points: 프론티어 샘플 개수
    """
    import numpy as np

    print("\n=== [EF] START efficient frontier ===", flush=True)

    if df.empty:
        print("[EF] ERROR: df is empty!", flush=True)
        return [], [], []

    risks = []
    returns = []
    weights_list = []

    grid = np.linspace(0.0, 1.0, n_points)
    print("[EF] grid:", grid, flush=True)

    for tr in grid:
        print(f"\n[EF] ---- target={tr:.3f} ----", flush=True)
        try:
            w, r, ret = compute_target_risk(df, tr)
            print(f"[EF] w: {w}", flush=True)
            print(f"[EF] risk={r}, ret={ret}", flush=True)

            if np.isfinite(r) and np.isfinite(ret):
                risks.append(float(r))
                returns.append(float(ret))
                weights_list.append(w.tolist())
            else:
                print("[EF] nan detected, skip", flush=True)

        except Exception as e:
            print(f"[EF] ERROR at target {tr}: {e}", flush=True)
            continue

    print("=== [EF] END efficient frontier ===\n", flush=True)
    return risks, returns, weights_list
