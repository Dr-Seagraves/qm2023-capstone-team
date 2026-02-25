[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634860&assignment_repo_type=AssignmentRepo)

# QM 2023 Capstone Project: Asset Class Divergence Analysis

Semester-long capstone for Statistics II: Data Analytics.

## Team Members
- Sam Weber - Data Engineer
- Brett Ragle - Analyst
- Anthony Ibarra - Visualizer

## Project Structure

- **code/** — Python scripts and notebooks. Use `config_paths.py` for paths.
- **data/raw/** — Original data (read-only)
- **data/processed/** — Intermediate cleaning outputs
- **data/final/** — M1 output: analysis-ready panel
- **results/figures/** — Visualizations
- **results/tables/** — Regression tables, summary stats
- **results/reports/** — Milestone memos
- **tests/** — Autograding test suite

Run `python code/config_paths.py` to verify paths.



## Research Question

What is driving the divergence between different asset classes (stocks, real estate, gold, and crypto), and how well can macroeconomic variables predict their relative performance? Additionally, how does asset pricing in alternative numeraires (e.g., S&P 500 priced in gold vs. USD) affect our understanding of their real returns?

## Dataset Overview

- **Primary Dataset:** Multiple asset price series from FRED and market data providers
- Entities: 4 asset classes (S&P 500, Case-Shiller home prices, gold spot, bitcoin) | Time: Monthly | Period: 2010-2024
- **Supplementary Data:**
  - Monetary Policy: M1, M2 (billions USD)
  - Interest Rates: Federal funds rate, Real rates (10Y), Yield curve slope
  - Inflation: CPI (median), PCE index
  - Economic Activity: US GDP (billions), Unemployment rate
  - Credit Conditions: BBB - Treasury spread
  - Risk & Sentiment: VIX index, Economic Policy Uncertainty index, Michigan Consumer Sentiment index

## Hypotheses (Preliminary)

1. Economic uncertainty (VIX, EPU) and interest rate changes significantly drive divergence between risky assets (stocks, crypto) and safe-haven assets (gold, real estate).
2. Monetary policy measures (M1, M2 growth) have differential effects on asset classes, with greater impact on inflation-sensitive and speculative assets.
3. Cross-asset pricing relationships remain stable despite price divergence, indicating fundamental differences in risk-adjusted return dynamics across asset classes.

## Repository Structure

```
qm2023-capstone-team/
├── AI_AUDIT_APPENDIX.md         # Audit documentation for AI-assisted work
├── M1_data_quality_report.md    # Data quality assessment report
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── code/                         # Data processing and analysis scripts
│   ├── config_paths.py           # Centralized path configuration
│   ├── fetch_all_fred_economic_data.py  # FRED economic data retrieval
│   ├── fetch_asset_prices.py     # Asset price data collection
│   ├── clean_and_merge.py        # Data cleaning and merging pipeline
│   └── __pycache__/
├── data/                         # Data storage
│   ├── raw/                      # Original data (read-only)
│   ├── processed/                # Cleaned intermediate datasets
│   └── final/                    # Analysis-ready merged panel
├── results/                      # Output directory
│   ├── figures/                  # Visualizations and plots
│   ├── tables/                   # Regression tables and summary statistics
│   └── reports/                  # Milestone memos and analysis reports
└── tests/                        # Autograding test suite
```

## How to Run

1. **Clone repository** and navigate to the project directory
2. **Open in GitHub Codespaces** (recommended environment)
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Fetch FRED economic data:** `python code/fetch_all_fred_economic_data.py`
5. **Fetch asset prices:** `python code/fetch_asset_prices.py`
6. **Clean and merge datasets:** `python code/clean_and_merge.py`
7. **Verify output:** Check `data/final/merged_analysis_panel.csv` for the analysis-ready dataset

**Path Verification:** Run `python code/config_paths.py` to verify all paths are correctly configured.