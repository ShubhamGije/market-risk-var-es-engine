# Market Risk VaR & Expected Shortfall — EUR/USD

## Overview

This project is an illustrative market risk analytics case study focused on EUR/USD exchange-rate risk.

The analysis estimates and compares downside risk using Historical, Parametric, and Monte Carlo approaches to Value at Risk (VaR) and Expected Shortfall (ES). It also includes stress testing, multi-horizon risk analysis, and illustrative portfolio-loss translation.

The project is designed to demonstrate practical application of market risk concepts using Python, statistical analysis, and financial data.

## Objectives

The project aims to:

- Estimate EUR/USD downside risk using VaR and Expected Shortfall.
- Compare Historical, Parametric, and Monte Carlo methodologies.
- Analyze risk at 95% and 99% confidence levels.
- Evaluate the impact of different risk horizons.
- Perform historical and hypothetical stress testing.
- Translate percentage-based risk measures into illustrative EUR portfolio losses.
- Interpret the results from a market risk management perspective.

## Methodologies

### Historical VaR & Expected Shortfall

Historical simulation uses the empirical distribution of observed EUR/USD returns without imposing a specific parametric distribution.

### Parametric VaR & Expected Shortfall

The parametric approach estimates risk using the historical mean and volatility of EUR/USD returns under a normal-distribution assumption.

### Monte Carlo VaR & Expected Shortfall

Monte Carlo simulation generates simulated returns using the historical mean and volatility under a normal-distribution assumption.

A fixed random seed is used to make the simulation reproducible.

### Stress Testing

The analysis evaluates both:

- Historical worst-day return
- Hypothetical market shocks of -1%, -2%, -3%, and -5%

### Multi-Horizon Risk Analysis

Historical risk is evaluated across:

- 1-day
- 10-day
- 21-day
- 252-day

The multi-day historical approach uses observed overlapping returns over each horizon and therefore represents an empirical historical-risk analysis rather than a full portfolio revaluation framework.

## Risk Measures

The project calculates:

- Historical VaR
- Historical Expected Shortfall
- Parametric VaR
- Parametric Expected Shortfall
- Monte Carlo VaR
- Monte Carlo Expected Shortfall

Risk estimates are evaluated at:

- 95% confidence level
- 99% confidence level

## Data

Daily EUR/USD exchange-rate data is obtained from Yahoo Finance using the `yfinance` Python library.

A five-year historical sample is used for the analysis. Closing exchange rates are used to calculate daily and multi-day EUR/USD returns.

EUR is used as the reporting and illustrative portfolio currency throughout the project.

The data is used for educational and portfolio-demonstration purposes and is not intended to represent production-grade market data.

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- yfinance
- Jupyter Notebook / Google Colab

## Project Structure

```text
market-risk-var-es-engine/
│
├── Market_Risk_VaR_ES_Case_Study.ipynb
└── README.md
