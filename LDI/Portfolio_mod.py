import pandas as pd
import numpy as np
import math
import risk_mod as rm

from  scipy.optimize import minimize

"""
This module contains various portfolio strategies 
"""

#=============================== Portfolio Return =========================================

def portfolio_return(weights, returns):
    """
    Computes the return on a portfolio from constituent returns and weights
    weights are a numpy array or Nx1 matrix and returns are a numpy array or Nx1 matrix
    """
    return weights.T @ returns


#=============================== Portfolio Volatility =========================================

def portfolio_vol(weights, covmat):
    """
    Computes the vol of a portfolio from a covariance matrix and constituent weights
    weights are a numpy array or N x 1 maxtrix and covmat is an N x N matrix
    """
    return (weights.T @ covmat @ weights)**0.5

#=============================== Efficient Frontier for TWO assets =========================================

def plot_ef(n_points, er, cov, style=".-"):
    """
    Plots the 2-asset efficient frontier
    """
    if er.shape[0] != 2 or er.shape[0] != 2:
        
        raise ValueError("plot_ef can only plot 2-asset frontiers")
        
    weights = [np.array([w, 1-w]) for w in np.linspace(0, 1, n_points)]
    
    rets = [portfolio_return(w, er) for w in weights]
    vols = [portfolio_vol(w, cov) for w in weights]
    
    ef   = pd.DataFrame({"Return":    rets, 
                         "Risk": vols})
    
    return ef.plot.line(x="Risk", y="Return", style=style, figsize=(8,5))


#=============================== Optimal Portfolio Problem =========================================


def minimize_vol(target_return, er, cov):
    """
    Returns the optimal weights that achieve the target return
    given a set of expected returns (er) and a covariance matrix (cov)
    """
    
    n          = er.shape[0]         # number of assets
    init_guess = np.repeat(1/n, n)   # an equally weighted portfolio of assets as the initial guess
    
    bounds = ((0.0, 1.0),) * n       # For all n assets, 0 <= w_i <= 1.0
    
    # construct the constraints
    weights_sum_to_1 = {'type': 'eq',
                        'fun' : lambda weights: np.sum(weights) - 1
    }
    
    return_is_target = {'type': 'eq',
                        'args': (er,),
                        'fun' : lambda weights, er: target_return - portfolio_return(weights, er)
    }
    
    weights = minimize(portfolio_vol, init_guess,
                       args        = (cov,),
                       method      = 'SLSQP',
                       options     = {'disp': False},
                       constraints = (weights_sum_to_1, return_is_target),
                       bounds      = bounds
                      )
    return weights.x


#=============================== Get Optimal Weights for all potential Retunrs =========================================

def optimal_weights(n_points, er, cov):
    """
    creates a linear space of returns as target retruns
    computes optimal weights that deliver that return
    returns a matrix of weight where each row is associated with a target return
    """
    target_rs = np.linspace(er.min(), er.max(), n_points)
    weights   = [minimize_vol(target_return, er, cov) for target_return in target_rs]
    
    return weights

#=============================== Efficient Frontier for Multiple assets =========================================


def plot_ef(n_points, er, cov, style = '.-'):
    """
    Plots the multi-asset efficient frontier
    """
    weights = optimal_weights(n_points, er, cov) 
    
    rets    = [portfolio_return(w, er) for w in weights]
    vols    = [portfolio_vol(w, cov)   for w in weights]
    
    ef      = pd.DataFrame({"Returns"   : rets,         
                            "Volatility": vols})
    
    return ef.plot.line(x = "Volatility", y = "Returns", style = style)



#=============================== Tangency or Maximum Sharpe Ration Portfolio =========================================


def msr(riskfree_rate, er, cov):
    """
    Returns the weights of the portfolio that gives you the maximum sharpe ratio
    given the riskfree rate and expected returns and a covariance matrix
    """
    n          = er.shape[0]         # number of assets
    init_guess = np.repeat(1/n, n)   # an equally weighted portfolio of assets as the initial guess
    
    bounds = ((0.0, 1.0),) * n       # For all n assets, 0 <= w_i <= 1.0
    
    # construct the constraints
    weights_sum_to_1 = {'type': 'eq',
                        'fun' : lambda weights: np.sum(weights) - 1
    }
    
    def neg_sharpe(weights, riskfree_rate, er, cov):
        """
        Returns the negative of the sharpe ratio
        of the given portfolio
        """
        r   = portfolio_return(weights, er)
        vol = portfolio_vol(weights, cov)
        return -(r - riskfree_rate)/vol
    
    weights = minimize(neg_sharpe, init_guess,
                       args        = (riskfree_rate, er, cov),
                       method      = 'SLSQP',
                       options     = {'disp': False},
                       constraints = (weights_sum_to_1,),
                       bounds      = bounds)
    return weights.x



#=============================== Efficient Frontier for Multiple assets with CML=========================================


def plot_ef_cml(n_points, er, cov, show_cml = False, style = '.-', riskfree_rate = 0):
    """
    Plots the multi-asset efficient frontier
    """
    weights = optimal_weights(n_points, er, cov) 
    
    rets    = [portfolio_return(w, er) for w in weights]
    vols    = [portfolio_vol(w, cov)   for w in weights]
    
    ef      = pd.DataFrame({"Returns"   : rets,         
                            "Volatility": vols})
    
    ax = ef.plot.line(x = "Volatility", y = "Returns", style = style)

    if show_cml:
        ax.set_xlim(left = 0)
        
        # get MSR
        w_msr   = msr(riskfree_rate, er, cov)
        r_msr   = portfolio_return(w_msr, er)
        vol_msr = portfolio_vol(w_msr, cov)
        
        # display CML
        cml_x = [0, vol_msr]
        cml_y = [riskfree_rate, r_msr]
        ax.plot(cml_x, cml_y, color='green', marker='o', linestyle='dashed', linewidth=2, markersize=12)
        
        return ax
    
#=============================== Efficient Frontier for Multiple assets with CML, EW =========================================

def plot_ef_cml_ew(n_points, er, cov, show_cml = False, show_ew = False, style = '.-', riskfree_rate = 0):
    """
    Plots the multi-asset efficient frontier
    """
    weights = optimal_weights(n_points, er, cov) 
    
    rets    = [portfolio_return(w, er) for w in weights]
    vols    = [portfolio_vol(w, cov)   for w in weights]
    
    ef      = pd.DataFrame({"Returns"   : rets,         
                            "Volatility": vols})
    
    ax = ef.plot.line(x = "Volatility", y = "Returns", style = style)
    
    if show_ew:
        n      = er.shape[0]
        w_ew   = np.repeat(1/n, n)
        r_ew   = portfolio_return(w_ew, er)
        vol_ew = portfolio_vol(w_ew, cov)
        
        # display EW
        ax.plot([vol_ew], [r_ew], color='goldenrod', marker='o', markersize=10)
        
    if show_cml:
        ax.set_xlim(left = 0)
        
        # get MSR
        w_msr   = msr(riskfree_rate, er, cov)
        r_msr   = portfolio_return(w_msr, er)
        vol_msr = portfolio_vol(w_msr, cov)
        
        # display CML
        cml_x = [0, vol_msr]
        cml_y = [riskfree_rate, r_msr]
        ax.plot(cml_x, cml_y, color='indianred', marker='o', linestyle='dashed', linewidth=2, markersize=12)
        
        return ax

#=============================== Global Minimum Volatility portfolio =========================================

def gmv(cov):
    """
    Returns the weights of the Global Minimum Volatility portfolio
    given a covariance matrix
    """
    n = cov.shape[0]
    return msr(0, np.repeat(1, n), cov)
    
#=============================== Efficient Frontier for Multiple assets with CML, EW, GMV =========================================

def plot_ef_cml_ew_gmv(n_points, er, cov, show_cml = False, show_ew = False, show_gmv = False, style = '.-', riskfree_rate = 0):
    """
    Plots the multi-asset efficient frontier
    """
    weights = optimal_weights(n_points, er, cov) 
    
    rets    = [portfolio_return(w, er) for w in weights]
    vols    = [portfolio_vol(w, cov)   for w in weights]
    
    ef      = pd.DataFrame({"Returns"   : rets,         
                            "Volatility": vols})
    
    
    ax = ef.plot.line(x = "Volatility", y = "Returns", style = style, title = "Optimal Portfolio Theory in practice",
                      label = 'Efficient Frontier', color = 'blue',  markersize = 7, figsize = (10,5))
    
    if show_ew:
        n      = er.shape[0]
        w_ew   = np.repeat(1/n, n)
        r_ew   = portfolio_return(w_ew, er)
        vol_ew = portfolio_vol(w_ew, cov)
        
        # display EW
        ax.plot([vol_ew], [r_ew], color='green', marker='o', markersize = 7, label = 'Eq. Weight')

    if show_gmv:
        w_gmv   = gmv(cov)
        r_gmv   = portfolio_return(w_gmv, er)
        vol_gmv = portfolio_vol(w_gmv, cov)
        
        # display GMV
        ax.plot([vol_gmv], [r_gmv], color='black', marker='o', markersize = 7, label = 'GMV')
        
        
    if show_cml:
        ax.set_xlim(left = 0)
        
        # get MSR
        w_msr   = msr(riskfree_rate, er, cov)
        r_msr   = portfolio_return(w_msr, er)
        vol_msr = portfolio_vol(w_msr, cov)
        
        # display CML
        cml_x = [0, vol_msr]
        cml_y = [riskfree_rate, r_msr]
        ax.plot(cml_x, cml_y, color='indianred', marker='o', linestyle='dashed', linewidth = 2, markersize = 7, label = 'CML')
        ax.legend()
        
        return ax


#=============================== Constant Proportion Portfolio Insurance =========================================

def run_cppi(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.03, drawdown = None):
    """
    Run a backtest of the CPPI strategy, given a set of returns for the risky asset
    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """
    
    # parameters
    dates         = risky_r.index
    n_steps       = len(dates)
    account_value = start
    floor_value   = start*floor
    peak          = start
    
    if isinstance(risky_r, pd.Series): 
        risky_r = pd.DataFrame(risky_r, columns=["R"])

    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/12 
        
    # DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    
    for step in range(n_steps):
        # dynamic floor
        if drawdown is not None:
            peak = np.maximum(peak, account_value)
            floor_value = peak*(1-drawdown)
            
        cushion = (account_value - floor_value)/account_value
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        safe_w  = 1-risky_w
        
        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w
        
        # recompute the new account value 
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step])
        
        # save the histories 
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        
        risky_wealth = start*(1+risky_r).cumprod()
        
    result = {
              "Wealth"           : account_history,
              "Risky Wealth"     : risky_wealth, 
              "Risk Budget"      : cushion_history,
              "Risky Allocation" : risky_w_history,
              "multiplier"       : m,
              "start"            : start,
              "floor"            : floor,
              "risky_r"          : risky_r,
              "safe_r"           : safe_r
    }
    return result



#=============================== Constant Proportion Portfolio Insurance (CPPI) =========================================

def run_cppi_cap(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.03, drawdown = None, cap = None):
    """
    Run a backtest of the CPPI strategy, given a set of returns for the risky asset
    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """
    cushion = risky_r.iloc[0].copy()
    cushion.values[:] = 0
    account_value = risky_r.iloc[0].copy()
    account_value.values[:] = start
    cap_value     = risky_r.iloc[0].copy()
    cap_value.values[:] = cap*start

    # parameters
    dates         = risky_r.index
    n_steps       = len(dates)
    floor_value   = start*floor
    peak          = start
    
    
        
    if isinstance(risky_r, pd.Series): 
        risky_r = pd.DataFrame(risky_r, columns=["R"])

    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/12 
        
    # DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    
    
    for step in range(n_steps):
        
        # dynamic floor            
        if drawdown is not None:
            peak = np.maximum(peak, account_value)
            floor_value = peak*(1-drawdown)
            
        cushion = (account_value - floor_value)/account_value

        # static cap
        if cap is not None:
            cushion[account_value >= (floor_value + cap_value)/2] = (cap_value - account_value)/account_value
              
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        safe_w  = 1-risky_w
                
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w                
        
        
        
        
        # recompute the new account value 
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step])
        
        # save the histories 
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        
        risky_wealth = start*(1+risky_r).cumprod()
        result = {
            "Wealth":           account_history,
            "Risky Wealth":     risky_wealth, 
            "Risk Budget":      cushion_history,
            "Risky Allocation": risky_w_history,
            "multiplier":       m,
            "start":            start,
            "floor":            floor,
            "risky_r":          risky_r,
            "safe_r":           safe_r
    }
    return result



#=============================== Cox-Ingersoll-Ross (CIR) Model =========================================

def cir(n_years = 10, n_scenarios = 1, a = 0.05, b = 0.03, sigma = 0.05, steps_per_year = 12, r_0 = None):
    """
    Inputs
    n_years        : planning horizon in years
    n_scenarios    : number of simulated paths
    a              : mean-reversion speed
    b              : average long-term annualized rate --- mean to revert to!
    sigma          : volatility of short term rate
    steps_per_year : frequency 
    r_0            : starting annualized rate
    
    output
    a dataframe of simulated paths for the "annualized" rate according to the CIR model
    
    """
    if r_0 is None: 
        r_0 = b 
        
    r_0 = rm.ann_to_inst(r_0)
    
    dt        = 1/steps_per_year
    num_steps = int(n_years*steps_per_year) + 1
    
    shock = np.random.normal(0, scale = np.sqrt(dt), size = (num_steps, n_scenarios))
    rates = np.empty_like(shock)
    
    rates[0] = r_0
    for step in range(1, num_steps):
        r_t         = rates[step-1]
        d_r_t       = a*(b-r_t)*dt + sigma*np.sqrt(r_t)*shock[step]
        rates[step] = abs(r_t + d_r_t)  
        
    return pd.DataFrame(data = rm.inst_to_ann(rates), index = range(num_steps))


#=============================== Price of Zero-Coupon Bond based on CIR Model =========================================

def zcb_cir(n_years = 10, n_scenarios = 1, a = 0.05, b = 0.03, sigma = 0.05, steps_per_year = 12, r_0 = None):
    """
    Inputs
    n_years        : planning horizon in years
    n_scenarios    : number of simulated paths
    a              : mean-reversion speed
    b              : average long-term annualized rate --- the mean to revert to!
    sigma          : volatility of short term rate
    steps_per_year : frequency 
    r_0            : starting annualized rate
    
    outputs
    rates : simulated paths for the "annualized" rate according to the CIR model
    prices: price of a zero-coupon bond according to the CIR model over simulated paths
    
    """

    if r_0 is None: 
        r_0 = b
        
    r_0 = rm.ann_to_inst(r_0)
    
    dt        = 1/steps_per_year
    num_steps = int(n_years*steps_per_year) + 1
    
    shock    = np.random.normal(0, scale = np.sqrt(dt), size = (num_steps, n_scenarios))
    rates    = np.empty_like(shock)
    rates[0] = r_0
    prices   = np.empty_like(shock) # simulated prices

    
    
    h = math.sqrt(a**2 + 2*sigma**2)
    
    def price_cir(ttm, r):
        """
        Inputs
        ttm: time-to-maturity (T-t)
        r  : short-term interest rate at time t
        
        Output
        price of a zero-coupon bond given ttm and r
        """
        A = ((2*h*math.exp((h+a)*ttm/2))/(2*h+(h+a)*(math.exp(h*ttm)-1)))**(2*a*b/sigma**2)
        B = (2*(math.exp(h*ttm)-1))/(2*h + (h+a)*(math.exp(h*ttm)-1))
        P = A*np.exp(-B*r)
        
        return P

    
    # initial prices
    prices[0] = price_cir(n_years, r_0)
    
    
    for step in range(1, num_steps):
        r_t   = rates[step-1]
        d_r_t = a*(b-r_t)*dt + sigma*np.sqrt(r_t)*shock[step]
        
        rates[step]  = abs(r_t + d_r_t)
        prices[step] = price_cir(n_years-step*dt, rates[step])

    rates  = pd.DataFrame(data = rm.inst_to_ann(rates), index = range(num_steps))
    prices = pd.DataFrame(data = prices, index = range(num_steps))

    return rates, prices


