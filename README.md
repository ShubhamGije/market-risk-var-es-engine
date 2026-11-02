# Market Risk VaR & Expected Shortfall Engine

This project is a practical market risk project that I built to understand how **Value at Risk (VaR)** and **Expected Shortfall (ES)** can be calculated and applied to a portfolio.

I started with a simple EUR/USD market risk case study and gradually developed it into a reusable Python risk engine and a multi-asset portfolio case study.

The project uses real market data and covers different approaches to measuring market risk.

---

## What this project covers

- Historical VaR
- Parametric VaR
- Monte Carlo VaR
- Historical Expected Shortfall
- Parametric Expected Shortfall
- Monte Carlo Expected Shortfall
- Stress testing
- Multiple confidence levels
- Multiple risk horizons
- Multi-asset portfolio risk
- Basic VaR backtesting
- Basel/FRTB-oriented Expected Shortfall concepts
- Illustrative liquidity horizon analysis

The project is mainly focused on **understanding the concepts and implementing them in Python**.

---

## Portfolio

The final case study uses five market risk factors:

- EUR/USD
- GBP/USD
- USD/JPY
- S&P 500
- Gold

The portfolio uses USD notionals for each risk factor.

Market data is downloaded dynamically, so the results can change when the notebook is run again with newer market data.

---

## Risk Measures

The project calculates VaR and Expected Shortfall at:

- 95% confidence level
- 97.5% confidence level
- 99% confidence level

It also looks at different horizons, including:

- 1 day
- 10 days
- 21 days
- 252 days

This helps compare how estimated risk changes with both confidence level and holding period.

---

## Basel / FRTB-Oriented Work

As an extension of the basic risk engine, I added some concepts related to the Basel market risk framework and FRTB.

This includes:

- 97.5% Expected Shortfall
- 10-day horizon
- Stress-period Expected Shortfall
- Illustrative liquidity horizon analysis
- Basic discussion of stressed risk measurement

These parts are **educational implementations** and are not intended to represent a complete regulatory FRTB capital calculation.

---

## Project Structure

```text
Market-Risk-VaR-ES-Engine/
│
├── EURUSD_Case_Study.ipynb
├── RiskEngine.py
├── Risk_Engine_Development.ipynb
├── Risk_Engine_Testing.ipynb
├── 01_Portfolio_Risk_Case_Study.ipynb
└── README.md
```

### Files

**EURUSD_Case_Study.ipynb**  
The starting point of the project. A focused EUR/USD case study covering VaR, Expected Shortfall and stress testing.

**RiskEngine.py**  
The reusable Python risk engine containing the main VaR, Expected Shortfall and stress testing calculations.

**Risk_Engine_Development.ipynb**  
Shows the development of the reusable risk engine.

**Risk_Engine_Testing.ipynb**  
Contains tests used to check the risk engine calculations and make sure the results behave as expected.

**01_Portfolio_Risk_Case_Study.ipynb**  
The main portfolio case study. It applies the risk engine to a multi-asset portfolio and extends the analysis toward Basel/FRTB concepts.

---

## Data

The project uses historical market data downloaded through Yahoo Finance.

Because the data is updated over time, the numerical results in the notebooks may change when they are run again.

The methodology and calculations remain the same.

---

## Tools Used

- Python
- Pandas
- NumPy
- SciPy
- Jupyter Notebook
- Matplotlib
- Seaborn
- Yahoo Finance market data

---

## What I Learned

Through this project, I worked on:

- Understanding different VaR methodologies
- Calculating Expected Shortfall
- Working with historical market data
- Understanding portfolio returns and risk
- Comparing different risk models
- Performing stress testing
- Understanding the importance of model testing
- Connecting practical risk calculations with Basel/FRTB concepts

This project is also a starting point for building more advanced market risk and risk analytics projects in the future.

---

## Disclaimer

This is an educational and portfolio project.

The calculations and Basel/FRTB-related sections are simplified implementations for learning purposes. They should not be treated as a complete regulatory capital model or production risk system.
