# Liability-Hedging and Insurance Investment: Monte-Carlo Simulations
<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/p0.png" width="900"/>

Modern Portfolio Theory emphasizes the importance of *diversification* where investor's can improve their reward-to-risk ratio. This theory shows how we can lower our exposure to unrewarded idiosyncratic risk by desinging a well-diversified portfolio. This approach, though very helpful, is not without any shortcomings. For example, diversification does not provide any protection against *systemic risk*. In other words, during market crashes, since the correlation of assets increases, it would be very difficult to protect investors' wealth by simply designing a diversified portfolio. 

In presence of a risk-free asset -such as government bonds- we can use investment strategies that guarantee certain outcomes. The `Constant Proportion Portfolio Insurance (CPPI)` is a frequently used investment approach that allows us to impose a lower bound to our return. In addition to that, a more comprehensive approach considers the fact that investors usually have time-bounded liabilities, which they must meet. The objective of a `Liability-Hedging Investment`, then, would be to ensure a matching-ratio between assets and liabilities in uncertain environments. This notebook introduces these concepts, implements them in `Python`, and then studies their performance through `Monte-Carlo Simulations`.

## An Overview of Simulation Results
### Constant Proportion Portfolio Insurance
<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/intro.png" width="450"/><img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/gbm.png" width="550"/>
While seeking higher returns is always important, a crucial aspect of an effective investment strategy is loss prevention. `Constant Proportion Portfolio Insurance (CPPI)` is an intuitive investment strategy that aims to achieve the second objective -*i.e.,* to protect investor's capital. Under CPPI, we target a minimum level of wealth that we can tolerate -*i.e.*, **protection floor**. For instance, we can set the floor to be at 80 percent of the initial capital. The CPPI strategy ensures that we do not violate this floor. The intuition behind this algorithm is to increase the risky investment in the portfolio during bull markets, and decrease it -by investing more in the risk-free asset- during bear markts. This is done so that if the decline in the risky asset price continues, we gradually reduce our investmnet in risky asset to a point we are no longer subject to risk so that the protection floor is not violated.

To demonstrate this strategy, I usehistorical monthly returns of the US Stock market obtained from [this](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) webpage, which starts from `1926-07` and runs through `2023-06`. I work with the 30 industry classification. 
<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/ms.png" width="600"/>

The CPPI algorithm requires asset allocation across `risky` and `rsikless` assets. In this simulation I consider the following assets:
* Risky Assets: a subset of industry indices
* Riskless Asset: an asset with a 3 percent return annually 
A bsic implementing of this algrithm requires (a) computing the cushion (asset value minus floor); and (b) computing the allocation to risky and riskless assets.

<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/cppi-1.png" width="450"/><img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/basic-1.png" width="450"/>

This basic algorithm, as seen above, results in a *significant* drop in drawdowns of assets, and lower volatilities. Then, I extend this algrothim. The basic algorithm of CPPI protects a fixed floor -e.g., in our previous example, this floor was 90 percent of our initial investment. However, this does not seem to be efficient; specially as over time, the value of our portfolio could grow so high than the floor. An alternative algorithm is the `drawdown-based CPPI` where we impose an explicit upper limit to our drawdown. In other words, our objective would be to ensure that the loss on the CPPI portfolio does not exceed the protected level. This is going to lead to a dynamic definition of the floor where instead of protecting a fixed wealth level, we shoulld protect an upper limit to our drawdon every period. For example, in the next example, I want to limit the drawdown to 15 percent. 

<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/dd-cppi.png" width="450"/><img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/dd-cap.png" width="450"/>

The second extension that I study here involves imposing a maximum to our portfolio strategy- as we discussed earlier. To implement this strategy, at each point, we should check which constraint is more likely to be binding: floor or cap. Based on that determination, the cushion and risky investment will be computed. 

<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/cnc.png" width="450"/><img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/gbm.png" width="450"/>

Then, I study the efficiency of the CPPI strategy in preventing floor violations in a simulation exercise. For this purpose, I first simulate multiple paths for the evolution of a risky asset -say, a stock price. Then, I build a CPPI portfolio using a risky and a riskless asset -say, government bonds, and verify whether under any circumstances the CPPI portfolio fails to protect the target floor. I use a random walk process to simulate risky asset prices. 

<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/sim-1.png" width="550"/>

<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/sim-2.png" width="650"/>
The interactive nature of this simulation, which use the `IPyWidgets` library in `Python` allows us to compare floor violations in various scenarios. This simulation shows that under realistic assumptions, we can lower floor violations to less than 0.01 percent. In addition to that:

* Higher values for the multiplier leads to more floor vilations and higher conditional shortfalls
* higher volatility leads more floor vilations and higher conditional shortfalls



### Liability-Hedging Investment


## Content
[1. Insurance Strategies: Constant Proportion Portfolio Insurance](#1)
    
   - [1.1.  CPPI: From Introduction to Implementation](#1.1)  
        * [Basic CPPI Algorthim ](#1.1.1)
        * [Extension: Drawdown-Based CPPI](#1.1.2) 
        * [Extension: CPPI with A Cap](#1.1.3)
          
   - [1.2. CPPI in Practice: A Monte-Carlo Simulation](#1.2) 
        * [A Brownian Motion for Stock Price ](#1.2.1)
        * [Floor Violation Analysis](#1.2.2)        
     &nbsp;
     
[2. Liability-Hedging Strategies through Asset Allocation](#2) 

   - [2.1. Short-Term Fluctuations: Cox-Ingersoll-Ross Model](#2.1) 
        * [Evolution of Liabilities](#2.1.1)
        * [Funding Ratio and the Interest Rate Risk](#2.1.2)  
    
   - [2.2. Investment, Liabilities, and Funding Ratio](#2.2) 
        * [Performance Seeking Portfolio (PSP) vs. Liability Hedging Portfolio (LHP)](#2.2.1)
        * [Duration-Matching Bond Portfolios](#2.2.2)
        * [Simulation of Coupon-Bearing Bonds](#2.2.3)
        * [Asset Allocation Problem: A Simulation](#2.2.4)
         

## Data
Two datasets used:
  1) monthly returns of the US Stock market obtained from [this](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) webpage
All data used are available in the "Data" folder of this repository.

 ## Code
 "CPPI.ipynb" + Auxiliary module "risk-mod".
