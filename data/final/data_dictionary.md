# Data Dictionary: Merged Economic Dataset

## Dataset Overview

| Property | Value |
|---|---|
| **Filename** | `merged_economic_data.csv` |
| **Entities** | 1 (US economy + USD asset markets) |
| **Time Periods** | 297 months |
| **Date Range** | 2001-02-28 to 2025-10-31 |
| **Time Span** | 24.7 years |
| **Frequency** | Monthly (month-end dates) |
| **Dimensions** | 297 rows × 17 columns |
| **File Size** | ~52 KB |

---

## Variable Definitions

| Variable | Description | Type | Source | Units | Notes |
|---|---|---|---|---|---|
| **date** | Month-end date | datetime | — | YYYY-MM-DD | Index variable; standardized to last trading day of month |
| **m1_billions** | M1 Money Stock | float | FRED (M1SL) | Billions USD | Narrow monetary aggregate; monthly observations |
| **m2_billions** | M2 Money Stock | float | FRED (M2SL) | Billions USD | Broad monetary aggregate; includes M1 + savings deposits |
| **fed_funds_rate** | Federal Funds Rate | float | FRED (DFF) | % per annum | Monthly average of daily rates; policy benchmark |
| **real_rate_10y** | Real Interest Rate (10Y) | float | FRED (REAINTRATREARAT10Y) | % per annum | Breakeven inflation rate; monthly observations |
| **yield_curve_slope** | Yield Curve Slope | float | FRED (T10Y2Y) | Percentage points | 10Y Treasury minus 2Y Treasury; monthly last value |
| **pce_index** | PCE Price Index | float | FRED (PCE) | Index (2017=100) | Personal consumption expenditure deflator |
| **cpi_median** | Median CPI | float | FRED (MEDCPIM158SFRBCLE) | % per annum | Median consumer price inflation |
| **gdp_billions** | Real GDP | float | FRED (GDP) | Billions USD (2017 chained) | Quarterly data forward-filled to monthly |
| **unemployment_rate** | Unemployment Rate | float | FRED (UNRATE) | % of labor force | Monthly civilian unemployment rate |
| **home_price_index** | Home Price Index | float | FRED (CSUSHPISA) | Index (1995 Q1=100) | Case-Shiller national residential index; monthly observations |
| **sp500_index** | S&P 500 Index | float | Yahoo Finance (^GSPC) | Index points | Daily closing prices aggregated to monthly last |
| **gold_price_usd** | Gold Futures Price | float | Yahoo Finance (GC=F) | USD per troy ounce | Continuous contract; monthly last value |
| **bitcoin_price_usd** | Bitcoin Price | float | Yahoo Finance (BTC-USD) | USD per coin | Available from 2014-09-17; pre-2014: NaN |
| **vix_index** | VIX Volatility Index | float | FRED (VIXCLS) | Index (volatility per annum) | CBOE Volatility Index; monthly mean |
| **epu_index** | Economic Policy Uncertainty Index | float | FRED (USEPUINDXD) | Index (1998=100) | Daily policy uncertainty; monthly mean |
| **consumer_sentiment** | Consumer Sentiment | float | FRED (UMCSENT) | Index (1966 Q1=100) | University of Michigan; monthly observations |

---

## Cleaning Decisions Summary

### Frequency Standardization
- **Daily data** (interest rates, prices, VIX, EPU): Aggregated to monthly using **last value at month-end** (market convention) or **mean** (for volatility/uncertainty indices)
- **Quarterly data** (GDP): Forward-filled to monthly (quarterly value repeated across 3 months)
- **Monthly data** (M1, M2, unemployment, CPI): Reindexed to month-end dates; no aggregation needed

### Missing Value Handling
| Variable | Raw Missing | Method | Justification |
|---|---|---|---|
| **Yield Curve Slope** | 548 | Forward/backward fill | Market closures; filled with trend continuity |
| **BBB Spread** | 94 | Forward/backward fill | Market closures; institutional investors expect continuity |
| **Home Price Index** | 144 | Forward/backward fill | Case-Shiller published monthly; gaps from publication schedule |
| **Bitcoin** | 163 (54.9% pre-2014) | Kept as NaN | Asset non-existence (not data quality issue) |
| **GDP** | 4 | Forward fill | Quarterly to monthly conversion |

### Outlier Treatment
- **No trimming or Winsorization applied** — All extreme values retained as they reflect real economic/market phenomena (financial crises, market crashes, policy shifts)

### Date Range Alignment
- **Anchor point**: 2001-02-26 (earliest date for S&P 500 & gold from Yahoo Finance)
- **End date**: 2025-10-31 (latest complete common month across all series)
- **Missing date gaps**: None; all 297 months present in sequence

### Special Cases
- **Bitcoin**: Available only from 2014-09-17 onwards (134 of 297 months; 45.1% complete)
  - Pre-2014 values are NaN (not filled) — Bitcoin didn't exist; appropriate for optional inclusion in regression analysis
- **VIX & EPU**: Aggregated as **monthly mean** (not last value) to smooth daily volatility
- **GDP**: Aggregated as **forward fill** to monthly (quarterly fixed; no monthly equivalent from FRED)

---

## Data Quality Flags

| Check | Status | Notes |
|---|---|---|
| No date gaps | ✓ Pass | 297 months in unbroken sequence |
| No duplicate rows | ✓ Pass | Unique date index |
| Complete (except Bitcoin) | ✓ Pass | 16/17 variables = 100% coverage; Bitcoin = 45.1% |
| Type consistency | ✓ Pass | All float64 or datetime64 |
| Logical value ranges | ✓ Pass | No negative prices; extremes reflect real events |
| Time-series ordering | ✓ Pass | Strictly chronological; monthly increment |
| Merge alignment | ✓ Pass | No misaligned columns |

---

## Reproducibility

To recreate this dataset:
```bash
python code/fetch_all_fred_economic_data.py   # Fetches 14 FRED series
python code/fetch_asset_prices.py              # Fetches Yahoo Finance data (S&P 500, gold, Bitcoin)
python code/create_final_dataset.py            # Cleans, resamples, aligns, merges
```

Output: `data/final/merged_economic_data.csv`

---

## Related Documentation

- [M1_data_quality_report.md](../M1_data_quality_report.md) — Comprehensive data sourcing, ethics, and reproducibility
- [missing_values_report.csv](./missing_values_report.csv) — Detailed imputation decisions by variable

---

**Data dictionary created:** 2026-02-24  
**Dataset version:** Final (v1.0)
