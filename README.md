# Liability-Hedging and Insurance Investment: Monte-Carlo Simulations
<img src="https://github.com/MohsenM-Git/Investments/blob/main/Images/p0.png" width="900"/>

Modern Portfolio Theory emphasizes the importance of *diversification* where investor's can improve their reward-to-risk ratio. This theory shows how we can lower our exposure to unrewarded idiosyncratic risk by desinging a well-diversified portfolio. This approach, though very helpful, is not without any shortcomings. For example, diversification does not provide any protection against *systemic risk*. In other words, during market crashes, since the correlation of assets increases, it would be very difficult to protect investors' wealth by simply designing a diversified portfolio. 

In presence of a risk-free asset -such as government bonds- we can use investment strategies that guarantee certain outcomes. The `Constant Proportion Portfolio Insurance (CPPI)` is a frequently used investment approach that allows us to impose a lower bound to our return. In addition to that, a more comprehensive approach considers the fact that investors usually have time-bounded liabilities, which they must meet. The objective of a `Liability-Hedging Investment`, then, would be to ensure a matching-ratio between assets and liabilities in uncertain environments. This notebook introduces these concepts, briefly, implements them in `Python`, and then studies their performance through `Monte-Carlo Simulations`.


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
         
## Simulation and Results




## Data
Two datasets used:
  1) monthly returns of the US Stock market obtained from [this](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) webpage
All data used are available in the "Data" folder of this repository.

 ## Code
 "CPPI.ipynb" + Auxiliary module "risk-mod".
