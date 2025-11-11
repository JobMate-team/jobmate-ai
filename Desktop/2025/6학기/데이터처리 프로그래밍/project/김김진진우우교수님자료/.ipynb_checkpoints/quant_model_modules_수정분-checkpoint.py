import pandas as pd
import numpy as np
import pypfopt

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import objective_functions

from scipy.optimize import minimize


def SectorMomentumRotationalTopRank(days_of_year:int, ext_num:int, rebal_periods:str, return_df :pd.DataFrame)->pd.DataFrame:
    """
    Sector momentum with rotational system
    
    - Reference: https://quantpedia.com/strategies/sector-momentum-rotational-system/
    - Method: Use ten sector ETFs. Pick 3 ETFs with the strongest 12-month momentum into your portfolio and weight them equally.
                Hold them for one month and then rebalance.
    
    :param days_of_year: int, if calader date base which is 365, or not which is 252
    :param ext_num: int, 모멘텀이 좋은 것들 중 상위 몇개를 추출할 것인가
    :param rebal_periods: str, 리밸런싱 주기
    :param return_df: pd.DataFrame, 섹터모멘텀로테이션을 위한 수익률 데이터프레임
    
    :return: Portfolio Weights.
    """
    mt = pr.pct_change(days_of_year).dropna()

    monthly_idx = pd.date_range(start=mt.index[0], end=mt.index[-1], freq=rebal_periods)
    monthly_idx = mt.index[mt.index.get_indexer(monthly_idx, method='bfill')]

    top_list = []
    for dt in monthly_idx:
        ext_index = mt.loc[dt].sort_values(ascending=False).index[:ext_num]
        top_list.append(ext_index)

    Pw = pd.DataFrame(index=monthly_idx, columns=mt.columns)

    for dt, indices in zip(monthly_idx, top_list):
        Pw.loc[dt, indices] = [1/ext_num]*ext_num

    Pw = Pw.fillna(0)
    
    return Pw


def EW(returns:pd.DataFrame, rebal_periods:str)->pd.DataFrame:    
    """
    Equan Weight Portfolio
    
    :param returns: pd.DataFrame, 수익률 데이터
    :param rebal_peridos: 리밸런싱 주기 설정
    
    :return: Equal Weights Portfolio
    """
    asset_num = len(returns.columns)

    rebal_indice = pd.date_range(returns.index[0], returns.index[-1], freq=rebal_periods) 
    rebal_indice = returns.index[returns.index.get_indexer(rebal_indice, method='ffill')]
    
    Pw = pd.DataFrame([[1/asset_num]*asset_num for i in range(len(rebal_indice))], index=rebal_indice, columns=returns.columns)
    return Pw


def MaximizeDiversification(rebal_periods: str, returns: pd.DataFrame, lookback_periods:int, bnd=None, long_only=True, frequency=252):    
    """
    Sector momentum with rotational system
    
    - Reference: https://quantpedia.com/strategies/sector-momentum-rotational-system/    
    
    :param rebal_periods: 리밸런싱 주기 설정, e.g. 'W-FRI', 'W-MON', 'BMS', ... pandas frequency 참조
    :param returns: 수익률 데이터
    :param lookback_periods: 공분산 계산시 몇일 짜리 공분산을 쓸 것인가. Operating days 기준임.
    :param bnd: Portfolio 가중치 제약조건
    :param long_only: Long only portfolio 여부, Short일 경우 False
    :param frequency: number of days in a year, calander base: 365 days operating base: 252 days
    
    :return: Portfolio Weights.
    """
    
    def calc_diversification_ratio(w, V):
        # avg weighted vol
        w_vol = np.dot(np.sqrt(np.diag(V)), w.T)
        # portfolio vol
        port_vol = np.sqrt(np.dot(np.array(w).T,np.dot(V,w)))
        diversification_ratio = w_vol/port_vol

        # return negative for minimization problem(maximize = minimize -)
        return -diversification_ratio

    def total_weight_constraint(x):
        return (x.sum() - 1.0)

    def long_only_constraint(x):
        return (x - 1.0)

    def get_weights(w0, V, bnd, long_only):
        # w0: initial weight, 추천: 동일비중으로 시작
        # V: covariance matrix
        # bnd: inidividual position limit
        # long only: long only constraint
        cons = ({'type': 'eq', 'fun': total_weight_constraint},)
        if long_only and bnd is None:
            bnd = ([(0,1) for i in range(len(w0))])
        res = minimize(calc_diversification_ratio, w0, bounds=bnd, args=V, method='SLSQP', constraints=cons)
        return clean_weights(res.x)
    
    w0 = [1/len(returns.columns)]*len(returns.columns)
    
    rebal_indice = pd.date_range(returns.index[0+lookback_periods], returns.index[-1], freq=rebal_periods)
    rebal_indice = returns.index[returns.index.get_indexer(rebal_indice, method='ffill')]
    
    Pw_list = []
    for idx in rebal_indice:
        ext_returns = returns.loc[:idx].iloc[-lookback_periods:]
        V = pypfopt.risk_models.sample_cov(ext_returns, returns_data=True, frequency=frequency)        
        W = get_weights(w0, V, bnd, long_only) # BOUND 설정파트
        Pw_list.append(W)
    Pw = pd.DataFrame(Pw_list, index=rebal_indice, columns=returns.columns)
    return Pw
    


def MeanVarianceMaxSharpe(rebal_periods:str, returns:pd.DataFrame, lookback_periods:int,  frequency=252):    
    """
    Mean-Varaince Optimization portfolio - Max Sharpe
    
    :param returns: pd.DataFrame, 수익률 데이터
    :param lookback_periods: 몇일 짜리 Covariance, Mu를 쓸것인가
    :param rebal_periods: str, 리밸런싱 주기
    :param frequeyncy: number of days in a year, calander base: 365 days operating base: 252 days
    
    :return: Portfolio Weights.    
    """
    try:
        rebal_indice = pd.date_range(returns.index[0+lookback_periods], returns.index[-1], freq=rebal_periods)
        rebal_indice = returns.index[returns.index.get_indexer(rebal_indice, method='ffill')]

        Pw_list = []
        for idx in rebal_indice:
            ext_df = returns.loc[:idx].iloc[-lookback_periods:]
            mu = expected_returns.mean_historical_return(ext_df, returns_data=True, compounding=True, frequency=frequency)
            S = risk_models.sample_cov(ext_df, returns_data=True, frequency=frequency)

            ef = EfficientFrontier(mu, S)
            res = ef.nonconvex_objective(objective_functions.sharpe_ratio,
                                             objective_args=(ef.expected_returns, ef.cov_matrix),
                                             weights_sum_to_one=True,)

            W = [res[i] for i in ef.clean_weights()]
            Pw_list.append(W)
        Pw = pd.DataFrame(Pw_list, rebal_indice, columns=returns.columns)
    except Exception as e:
        print(e)
        raise
    
    return Pw


def MeanVarianceMinVolatility(rebal_periods:str, returns:pd.DataFrame, lookback_periods:int, frequency=252):    
    """
    Mean-Varaince Optimization portfolio - Max Sharpe
    
    :param returns: pd.DataFrame, 수익률 데이터
    :param lookback_periods: 몇일 짜리 Covariance, Mu를 쓸것인가
    :param rebal_periods: str, 리밸런싱 주기
    :param frequeyncy: number of days in a year, calander base: 365 days operating base: 252 days
    
    :return: Portfolio Weights.    
    """
    

    rebal_indice = pd.date_range(returns.index[0+lookback_periods], returns.index[-1], freq=rebal_periods)
    rebal_indice = returns.index[returns.index.get_indexer(rebal_indice, method='ffill')]

    Pw_list = []
    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]
        mu = expected_returns.mean_historical_return(ext_df, returns_data=True, compounding=True, frequency=frequency)
        S = risk_models.sample_cov(ext_df, returns_data=True, frequency=frequency)

        ef = EfficientFrontier(mu, S)
        res = ef.min_volatility()

        W = [res[i] for i in ef.clean_weights()]
        Pw_list.append(W)
    Pw = pd.DataFrame(Pw_list, rebal_indice, columns=returns.columns)
    
    return Pw


def clean_weights(weights, cutoff=1e-4, rounding=5):
        """
        Helper method to clean the raw weights, setting any weights whose absolute
        values are below the cutoff to zero, and rounding the rest.

        :param cutoff: the lower bound, defaults to 1e-4
        :type cutoff: float, optional
        :param rounding: number of decimal places to round the weights, defaults to 5.
                         Set to None if rounding is not desired.
        :type rounding: int, optional
        :return: asset weights
        :rtype: OrderedDict
        """
        if weights is None:
            raise AttributeError("Weights not yet computed")
        clean_weights = weights.copy()
        clean_weights[np.abs(clean_weights) < cutoff] = 0
        if rounding is not None:
            if not isinstance(rounding, int) or rounding < 1:
                raise ValueError("rounding must be a positive integer")
            clean_weights = np.round(clean_weights, rounding)

        return clean_weights
    
    
def RP(rebal_periods:str, returns:pd.DataFrame, lookback_periods:int, frequency=252, cov_type='simple'):
    """
    Risk Parity Model
    
    :param rebal_periods: str, 리밸런싱 주기
    :param returns: pd.DataFrame, 수익률 데이터        
    :param lookback_periods: 몇일 짜리 Covariance, Mu를 쓸것인가    
    :param frequeyncy: number of days in a year, calander base: 365 days operating base: 252 days
    :param cov_type: Risk Parity Weight 계산시 사용할 공분산 매트릭스 타입.
    
    :return: Portfolio Weights.    
    """
    
    def get_weights(rets: pd.DataFrame, freq: int, cov_type, covariance=None):
        """
        Make RP portfolio which is long only portfolio.

            Parameters
        ----------
        rets: pd.DataFrame
            상품 수익률 데이터

        freq: str
            수익률 데이터의 주기

        cov_type: str
            covariance type, Now you can select in 'simple' or 'exponential'

        covariance: pd.DataFrame
            simple or exponential covariance를 제외한 다른 covariance matrix 사용시 사용.

        """
        from scipy.optimize import minimize
        from pypfopt.risk_models import exp_cov

        def RC(weight, covmat):
            weight = np.array(weigt)
            variance = wieght.T @ covmat @ weight
            sigma = variance ** 0.5
            mrc = 1/sigma * (covmat@weight)
            rc =weight * mrc
            rc = rc/rc.sum()

            return rc

        def RiskParity_objective(x):
            variance = x.T @ covmat @ x
            sigma = variance ** 0.5

            mrc = 1/sigma * (covmat @ x)
            rc = x * mrc
            a = np.reshape(rc, (len(rc), 1))
            risk_diffs = a - a.T
            sum_risk_diffs_squared = np.sum(np.square(np.ravel(risk_diffs)))
            return (sum_risk_diffs_squared)

        def weight_sum_constraint(x) :
            return(x.sum() - 1.0 )


        def weight_longonly(x) :
            return(x)

        if covariance is not None:
            covmat = covariance

        else:
            if cov_type == "simple":
                covmat = rets.cov().values

            elif cov_type == "exponential":
                covmat = exp_cov(rets,
                                 returns_data=True, 
                                 span=len(rets),
                                 frequency=frequency).values

        x0 = np.repeat(1/covmat.shape[1], covmat.shape[1]) 
        constraints = ({'type': 'eq', 'fun': weight_sum_constraint},
                      {'type': 'ineq', 'fun': weight_longonly})
        options = {'ftol': 1e-20, 'maxiter': 800}

        result = minimize(fun = RiskParity_objective,
                          x0 = x0,
                          method = 'SLSQP',
                          constraints = constraints,
                          options = options)
        return result.x
    
    rebal_indice = pd.date_range(returns.index[0+lookback_periods],
                                 returns.index[-1], freq=rebal_periods)

    rebal_indice = returns.index[returns.index.get_indexer(rebal_indice,
                                                           method='ffill')]

    Pw_list = []
    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]
        W = get_weights(ext_df, freq=frequency, cov_type=cov_type)    

        Pw_list.append(W)
    Pw = pd.DataFrame(Pw_list, rebal_indice, columns=returns.columns)
    return Pw

def RB(rebal_periods:str, returns:pd.DataFrame, lookback_periods:int, frequency=252, cov_type='simple', rb=None):
    """
    Risk Budget Model
    
    :param rebal_periods: str, 리밸런싱 주기
    :param returns: pd.DataFrame, 수익률 데이터        
    :param lookback_periods: 몇일 짜리 Covariance, Mu를 쓸것인가    
    :param frequeyncy: number of days in a year, calander base: 365 days operating base: 252 days
    :param cov_type: Risk Parity Weight 계산시 사용할 공분산 매트릭스 타입.
    
    :return: Portfolio Weights.        
    """
    
    from scipy.optimize import minimize
    from pypfopt.risk_models import exp_cov
    def obj_fun(x, p_cov, rb):
        # risk budgeting approach optimisation object function
        return np.sum((x*np.dot(p_cov,x)/np.dot(x.transpose(), np.dot(p_cov, x))-rb)**2)

    def cons_sum_weight(x):
        # constraint on sum of weights equal to one
        return np.sum(x) - 1.0

    def cons_long_only_weight(x):
        # constraint on weight larger than zero
        return x

    def get_weights(asset_rets, rb:list, cov_type:str):
        """
        :param asset_rets: 수익률 데이터
        :param rb: List, Risk Budget list
        """
        # number of ARP series
        num_arp = asset_rets.shape[1]

        # covariance matrix of asset returns
        if cov_type == "simple":
                p_cov = asset_rets.cov().values

        elif cov_type == "exponential":
            p_cov = exp_cov(asset_rets,
                             returns_data=True, 
                             span=len(rets),
                             frequency=frequency).values
        

        # initial weights
        w0 = 1.0 * np.ones((num_arp, 1)) / num_arp

        # constraints
        cons = ({'type': 'eq', 'fun':cons_sum_weight},
                {'type': 'ineq', 'fun':cons_long_only_weight})

        # portfolio optimisation
        res = minimize(obj_fun, w0, args=(p_cov, rb), method='SLSQP', constraints=cons)
        return res.x

    if rb is None:
        rb = [1/len(returns.columns)]*len(returns.columns)
    else:
        rb=rb

    rebal_indice = pd.date_range(returns.index[0+lookback_periods],
                                     returns.index[-1], freq=rebal_periods)

    rebal_indice = returns.index[returns.index.get_indexer(rebal_indice,
                                                           method='ffill')]

    Pw_list = []
    for idx in rebal_indice:
        ext_df = returns.loc[:idx].iloc[-lookback_periods:]
        W = get_weights(ext_df, rb, cov_type)    

        Pw_list.append(W)

    Pw = pd.DataFrame(Pw_list, rebal_indice, columns=returns.columns)
    return Pw