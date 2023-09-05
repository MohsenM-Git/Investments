import pandas as pd
import numpy as np
import math

from  scipy.optimize import minimize
from scipy.stats import norm
#=============================== Compounding Returns =========================================

def compound(r):
    """
    returns the result of compounding the set of returns in r
    """
    return np.expm1(np.log1p(r).sum())


#=============================== Number of Periods in a year =========================================

def periods_per_year(df):
    """
    returns periods_per_year for a dataframe
    """
    #  the index must be a datetime object! 
    # df.index.year.unique().values[1] chooses the second year, which hopefully is a complete year
    
    return df.iloc[df.index.year == df.index.year.unique().values[1], 0].count()


#=============================== Annualize Returns =========================================


def annualize_rets(r, periods_per_year):
    """
    Annualizes a set of returns
    """
    compound_ret = (1+r).prod()
    n_periods = r.shape[0]
    return compound_ret**(periods_per_year/n_periods)-1


#=============================== Annualize Volatility =========================================


def annualize_vol(r, periods_per_year):
    """
    Annualizes the vol of a set of returns
    """
    return r.std()*(periods_per_year**0.5)


#=============================== Sharpe Ratio =========================================


def sharpe_ratio(r, riskfree_rate, periods_per_year):
    """
    Computes the annualized sharpe ratio of a set of returns
    """
    # convert the annual riskfree rate to per period
    rf_per_period = (1+riskfree_rate)**(1/periods_per_year)-1
    excess_ret = r - rf_per_period
    ann_ex_ret = annualize_rets(excess_ret, periods_per_year)
    ann_vol = annualize_vol(r, periods_per_year)
    return ann_ex_ret/ann_vol


#=============================== DRAWDOWNS =========================================

def drawdown(returns_series: pd.Series, intitial_wealth = 100):
    """Takes 
        1. a time series of asset returns
        2. initial wealth
       returns
           a DataFrame with columns for
           1. the wealth index, 
           2. the previous peaks 
           3. the percentage drawdown
    """
    wealth_index   = intitial_wealth*(1+returns_series).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns      = (wealth_index - previous_peaks)/previous_peaks
     
    output = pd.DataFrame({"Wealth":        wealth_index, 
                           "Previous Peak": previous_peaks, 
                           "Drawdown":      drawdowns})
    
    return output

#=============================== Skewness ========================================

def myskewness(r):
    """
    Alternative to scipy.stats.skew()
    Computes the skewness of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**3).mean()
    return exp/sigma_r**3

#=============================== Kurtosis =========================================
def mykurtosis(r):
    """
    Alternative to scipy.stats.kurtosis()
    Computes the kurtosis of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**4).mean()
    return exp/sigma_r**4

#=============================== SEMIDEVIATION =========================================

def semideviation(r):
    """
    input: a Series or a DataFrame 'r'
    output: Returns the semideviation aka negative semideviation of r
    
    """
    is_negative = r < 0
    return r[is_negative].std(ddof=0)


#=============================== Historical VaR =========================================

def var_historic(r, level=5):
    """
    Returns the historic Value at Risk at a specified level 
    """
    if isinstance(r, pd.DataFrame):
        return r.aggregate(var_historic, level=level)
    elif isinstance(r, pd.Series):
        return -np.percentile(r, level)
    else:
        raise TypeError("Expected the input to be a Series or DataFrame")   
        

#=============================== Historical CVaR =========================================

def cvar_historic(r, level=5):
    """
    Returns the historic CVaR given a level that determines VaR.  
    """
    if isinstance(r, pd.DataFrame):
        return r.aggregate(cvar_historic, level=level)
    elif isinstance(r, pd.Series):
        is_lower = r<= -var_historic(r, level = level)
        return -r[is_lower].mean()
    else:
        raise TypeError("Expected the input to be a Series or DataFrame")  
        
        
#=============================== Gaussian VaR =========================================

def var_gaussian(r, level=5):
    """
    Returns the Parametric Gauusian VaR of a Series or DataFrame
    """
    # compute the Z score assuming it was Gaussian
    z = norm.ppf(level/100)
    return -(r.mean() + z*r.std(ddof=0))



#=============================== Semiparametric VaR: Cornish-Fisher =========================================

def var_parametric(r, level=5, modified=False):
    """
      Returns either
     * the Parametric Gauusian VaR of a Series or DataFrame,
     or if "modified = True",
     * the the Cornish-Fisher modified VaR 
    """
    # compute the Gaussian Z score 
    
    z = norm.ppf(level/100)
    
    if modified:
        
        s = myskewness(r)
        k = mykurtosis(r)
        z = (z +
                (z**2 - 1)*s/6 +
                (z**3 -3*z)*(k-3)/24 -
                (2*z**3 - 5*z)*(s**2)/36
            )
        
    return -(r.mean() + z*r.std(ddof=0))


#=============================== Summary Stats =========================================
def summary_stats(r, freq = 12, riskfree_rate = 0.03, rn = 3):
    """
    Return a DataFrame that contains aggregated summary stats for the returns in the columns of r
    """
    
    ann_r      = r.aggregate(annualize_rets, periods_per_year = freq)
    ann_vol    = r.aggregate(annualize_vol, periods_per_year = freq)
    skew       = r.aggregate(myskewness)
    kurt       = r.aggregate(mykurtosis)
    cf_var5    = r.aggregate(var_parametric, modified=True)
    hist_cvar5 = r.aggregate(cvar_historic)
    ann_sr     = r.aggregate(sharpe_ratio, riskfree_rate = riskfree_rate, periods_per_year = freq)
    dd         = r.aggregate(lambda r: drawdown(r).Drawdown.min())    
    
    
    return pd.DataFrame({
        "Annualized Return": np.round(100*ann_r, rn),
        "Ann. Volatility": np.round(100*ann_vol, rn),
        "Skewness": np.round(skew, rn),
        "Kurtosis": np.round(kurt, rn),
        "Cornish-Fisher VaR (5%)": np.round(100*cf_var5, rn),
        "Historic VaR (5%)":  np.round(100*hist_cvar5, rn),
        "Sharpe Ratio": np.round(ann_r, rn),
        "Max Drawdown": np.round(100*dd, rn),
    })


#=============================== General Browninan Motion =========================================
def gbm(n_years = 10, n_scenarios = 1000, mu = 0.07, sigma = 0.15, steps_per_year = 12, x_0 = 100.0, prices = True):
    """
    Evolution of Geometric Brownian Motion trajectories, such as for Stock Prices
    
    n_years        : The number of years to generate data for
    n_scenarios    : The number of scenarios
    mu             : Annualized Drift, e.g. Market Return
    sigma          : Annualized Volatility
    steps_per_year : granularity of the simulation
    x_0            : initial value of asset
    
    returns: a numpy array of n_paths columns and n_years*steps_per_year rows
    """
    
    # per-step Parameters
    dt      = 1/steps_per_year
    n_steps = int(n_years*steps_per_year)
    
    # two steps 
    #     xi      = np.random.normal(size=(n_steps, n_scenarios))
    #     rets    = mu*dt + sigma*np.sqrt(dt)*xi
    #  can combine them for more efficiency and create returns in one step with 
    # rets_plus_1 = np.random.normal(loc=(1 + mu*dt), scale=(sigma*np.sqrt(dt)), size=(n_steps, n_scenarios))

    # a more accurate way is to compund returns over the prtiod of dt, which means  
    rets_plus_1 = np.random.normal(loc=(1+mu)**dt, scale=(sigma*np.sqrt(dt)), size=(n_steps, n_scenarios))
    
    #   for illustrative purposes, start from the starting price    
    rets_plus_1[0] = 1
    price = x_0*pd.DataFrame(rets_plus_1).cumprod() if prices else rets_plus_1-1
    return price

#=============================== Discount Factor =========================================

def discount(t, r):
    """
    Computes discount rate at time t with r as the interest rate
    Note: both t and r should have the same frequency. For instance, quarterly or annually 
    """
    return (1+r)**(-t)

#=============================== Present Value =========================================

def pv(l, r):
    """
    Compute the present value of a list of cash flows 
    l : values indexed by time
    r : interest rate 
    
    output: the present value
    """
    dates = l.index
    discounts = discount(dates, r)
    
    return (discounts*l).sum()

#=============================== Funding Ratio-1 =========================================

def funding_ratio(assets, liabilities, r):
    """
    inputs
        current value of assets (not to be discounted)
        a series of liabilities
        interest rate
    
    returns
        the funding ratio based on the interest rate 
    """
    return assets/pv(liabilities, r)

#=============================== Funding Ratio-2 =========================================


def funding_ratio2(assets, liabilities, r):
    """
    inputs
        current value of assets (to be discounted)
        a series of liabilities
        interest rate
    
    returns
        the funding ratio based on the interest rate
    """
    return pv(assets, r)/pv(liabilities, r)

#=============================== instantaneous-to-annual interest rate =========================================

def inst_to_ann(r):
    """
    Convert an instantaneous rate to an annual interest rate
    """
    return np.expm1(r)

#=============================== annual-to-instantaneous interest rate  =========================================


def ann_to_inst(r):
    """
    Convert an annual rate to an instantaneous interest rate 
    """
    return np.log1p(r)


#=============================== Construct Cash Flow of a Bond =========================================


def cf_construct(maturity = 10, principal = 100, coupon_rate = 0.03, coupons_per_year = 12):
    """
    Inputs
        maturity of the bond in years
        principal of the bond
        coupon_rate: interest paid on principle annually 
        coupons_per_year
    
    
    Returns 
        A series of cash flows indexed by the payment number
    """
    
    n_coupons  = round(maturity*coupons_per_year)
    coupon_pay = principal*coupon_rate/coupons_per_year
    pay_number = np.arange(1, n_coupons+1)
    cash_flow  = pd.Series(data = coupon_pay, index = pay_number)
    
    cash_flow.iloc[-1] = cash_flow.iloc[-1] + principal # add the principal to the last payment
    return cash_flow


#=============================== Price of a zero-coupon bond =========================================


def bond_price(maturity = 10, principal = 100, coupon_rate = 0.03, coupons_per_year = 12, discount_rate = 0.03):
    """
    Inputs
        maturity of the bond in years
        principal of the bond
        coupon_rate: interest paid on principle annually 
        coupons_per_year
        discount_rate: in general, this is the yield curve
    
    Returns 
        price of bond 
    """
    cash_flow = cf_construct(maturity, principal, coupon_rate, coupons_per_year)
    return pv(cash_flow, discount_rate/coupons_per_year)


#=============================== Macaulay Duration of a Cash Flow =========================================


def macaulay_duration(cf, discount_rate):
    """
    Input
        cf: cash flow sequence
        discount_rate: discount rate matching the frequency of cash flow sequence
    
    return
        the Macaulay Duration 
    """
    disct_cf = discount(cf.index, discount_rate)*cf

    return (cf.index*disct_cf).sum()/disct_cf.sum()

#=============================== Matching Duration Portfolio =========================================


def matching_weights(cf_1, cf_2, cf_l, discount_rate):
    """
    Inputs
        cf_1: cash flow of bond 1 (short maturity)
        cf_2: cash flow of bond 2 (long maturity)
        cf_l: cash flow of liabilities
    
    Returns 
        weight of bond 1 to match the effective duration liabilities
    """
    d_1 = macaulay_duration(cf_1, discount_rate)
    d_2 = macaulay_duration(cf_2, discount_rate)
    d_l = macaulay_duration(cf_l, discount_rate)
    
    return (d_2 - d_l)/(d_2 - d_1)

#=============================== Simulate Price of a coupon-paying bond =========================================


def bond_price_sim(rates, maturity, principal, coupon_rate, coupons_per_year):
    """
    Inputs
    rates: a dataframe of simulated short term interest rates
    maturity
    principal
    coupon_rate
    coupons_per_year
    
    output
    a dataframe of price of a coupon-bearing bond over each simulated path for short term rate
    """

    bondp = pd.DataFrame().reindex_like(rates)

    for i in bondp.index:
        for j in bondp:
            if maturity - i/coupons_per_year <= 0:
                bondp.loc[i,j] = principal + principal*coupon_rate/coupons_per_year        
            else:
                bondp.loc[i,j] = bond_price(maturity - i/coupons_per_year, principal, coupon_rate, coupons_per_year, rates.loc[i,j])
    
    return bondp


#=============================== Return of a coupon-paying bond =========================================

def bond_return(bondp, principal, coupon_rate, coupons_per_year):
    """
    Inputs
    bondp: a dataframe of bond prices
    principal
    coupon_rate
    coupons_per_year
    
    output: 
    annualized return of bond on each price path 
    """

    coupon = principal*coupon_rate/coupons_per_year
    bondr  = pd.DataFrame().reindex_like(bondp)

    for i in range(1, len(bondp.index)):
        for j in bondr:
            bondr.loc[i,j] = (bondp.loc[i,j] + coupon)/bondp.loc[i-1,j] - 1 

    return annualize_rets(bondr.dropna(), 12)