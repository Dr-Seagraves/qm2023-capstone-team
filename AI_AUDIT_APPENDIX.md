# AI Audit Appendix (Assignment 05)

## Tool(s) Used
- GitHub Copilot (Claude Haiku 4.5)

## Task(s) Where AI Was Used
1. **Task 1:** Data Collection — Fetching economic data from FRED API and asset prices from Yahoo Finance
2. **Task 2:** Data Cleaning & Merging — Creating consolidated dataset with standardized frequency and alignment
3. **Task 3:** Report Generation — Creating data quality documentation and data dictionary
4. **Task 4:** EDA Notebook Generation — Building and iteratively refining `capstone_eda.ipynb` with 8 required M2 visualizations
5. **Task 5:** EDA Summary Generation — Creating `M2_EDA_summary.md` with findings, hypotheses, and data-quality flags for M3

## Key Prompts by Task

### Task 1: Data Collection
1. "create a script to fetch M1 monetary supply data from FRED"
2. "Create scripts for the following data from FRED: DFF, REAINTRATREARAT10Y, T10Y2Y, PCE, CPI, GDP, UNRATE, VIXCLS, USEPUINDXD, BAMLC0A4CBBB, UMCSENT"
3. "use MEDCPIM158SFRBCLE for CPI and add CSUSHPISA for home prices"
4. "create a new script to pull gold spot price from alpha vantage with historical data (25 years)"
5. "try yahoo finance instead" [After Alpha Vantage limitation discovered]
6. "edit the scripts to pull bitcoin and s&p 500 from yahoo finance, merge the data going all the way back to the beginning of the gold data"

### Task 2: Data Cleaning & Merging
1. "create a script that loads all raw CSV files from data/raw, standardizes them to monthly frequency, handles missing values, and creates a final merged dataset"
2. "bitcoin didn't exist before 2014—keep those as NaN, don't impute"
3. "extend the date range back to the earliest start date (February 2001 from gold data)"

### Task 3: Report Generation
1. "create a comprehensive data quality report documenting all data sources, cleaning decisions, and merge strategy"
2. "the yahoo data is the primary data, the fred is supplementary"
3. "create a data dictionary in data/final/data_dictionary.md with variable definitions and cleaning summary"

### Task 4: EDA Notebook Generation
1. "reference the M2 instructions document and the readme for our research question to create a jupiter notebook creating the 8 necessary figures"
2. "please make sure the seaborn colorblind friendly palletts are being used for all plots. Please write a short 1 sentence narrative explanation before each visualization (before the code). when creating the divergence index please write a 1 sentence explanation for why bitcoin was dropped"

### Task 5: EDA Summary Generation
1. "Create this into reports: 3. Summary Markdown: M2_EDA_summary.md"
2. "Required sections: Key Findings, Hypotheses for M3, Data Quality Flags"
3. "include correlations, optimal lag, group sensitivity, outliers, control patterns, and planned M3 mitigations"


## Output Summary

### Task 1: Data Collection

**Primary Data Source (Yahoo Finance):**
- Created `fetch_asset_prices.py` to fetch S&P 500, gold, and Bitcoin
- S&P 500 (^GSPC): 6,286 daily observations from 2001-02-26
- Gold (GC=F): 6,273 daily observations from 2001-02-26
- Bitcoin (BTC-USD): 4,179 daily observations from 2014-09-17
- All saved to `data/raw/` as CSV files

**Supplementary Data Source (FRED API):**
- Created `fetch_all_fred_economic_data.py` to fetch 14 economic indicators:
  - Monetary aggregates: M1 Money Stock, M2 Money Stock
  - Interest rates: Federal Funds Rate, Real Interest Rate (10Y), Yield Curve Slope
  - Inflation: PCE Price Index, Median CPI
  - Real economy: Real GDP, Unemployment Rate, Home Price Index
  - Market indicators: VIX, Economic Policy Uncertainty Index, BBB Spread, Consumer Sentiment
- All 14 series saved to `data/raw/` as CSV files

**Supporting infrastructure:**
- `.env` and `.env.example` files for secure API key management
- `.gitignore` to protect credentials
- `requirements.txt` for dependency tracking

---

### Task 2: Data Cleaning & Merging

**Created `create_final_dataset.py` to:**
- Load all 17 raw CSV files (14 FRED + 3 Yahoo Finance)
- Standardize frequency to monthly:
  - Daily data: Last value of month (prices, rates)
  - Daily volatility index: Mean of month (VIX, EPU)
  - Quarterly data: Forward-fill to monthly (GDP)
- Handle missing values:
  - Market closures: Forward/backward fill (548 yield curve, 94 BBB spread, etc.)
  - Bitcoin pre-2014: Keep as NaN (asset non-existence, not data quality issue)
- Align all datasets to common date range (2001-02-28 to 2025-10-31)
- Save individual processed files to `data/processed/`
- Merge into single dataset: `data/final/merged_economic_data.csv`

**Final dataset:**
- Shape: 297 rows × 17 columns
- Coverage: 24.7 years of monthly data
- Bitcoin completeness: 45.1% (134/297 months; NaN pre-2014 by design)
- All other variables: 100% complete

---

### Task 3: Report Generation

**Created `M1_data_quality_report.md` (476 lines):**
- Comprehensive documentation of all data sources, frequencies, and coverage
- Detailed cleaning decisions for each variable
- Merge strategy and join verification
- Data balance analysis and quality flags
- Reproducibility checklist for dataset recreation
- Ethical considerations (data exclusions, bias, Bitcoin inclusion rationale)

**Created `data/final/data_dictionary.md`:**
- Dataset overview (1 entity, 297 time periods, 24.7 years)
- Variable definitions table (all 17 variables with source, type, units)
- Cleaning decisions summary (frequency standardization, missing value handling)
- Data quality flags and reproducibility instructions

---

### Task 4: EDA Notebook Generation

**Created `code/capstone_eda.ipynb` to satisfy M2 visualization requirements:**
- Built all 8 required EDA plots and saved outputs to `results/figures/`
- Defined divergence outcome as cross-asset return dispersion (S&P 500, Home Price Index, Gold), with Bitcoin excluded from construction due to limited historical coverage
- Added plot-specific interpretation captions tied to M2 guidance (correlation structure, lag structure, group sensitivity, control relationships, decomposition)

**Major iterative refinements made after initial generation:**
- Resolved notebook execution issues (kernel state/order-of-execution fixes)
- Added Plot 3 moving-average overlay and adjusted z-order (divergence base, MA overlay, Fed Funds line)
- Repositioned Plot 3 legend to avoid data occlusion
- Added slope-labeled legends to Plot 7 regression lines
- Standardized chart styling to seaborn colorblind-friendly palette across plots
- Added one-sentence narrative lead-ins before each visualization section
- Updated Plot 8 labeling (Year x-axis label and `Divergence Index` naming)
- Consolidated duplicate notebook copies so only `code/capstone_eda.ipynb` remains

---

### Task 5: EDA Summary Generation

**Created `results/reports/M2_EDA_summary.md`:**
- Included required sections: Key Findings, Hypotheses for M3 (3+), and Data Quality Flags
- Reported evidence-backed findings on:
  - Correlations (e.g., VIX strongest with divergence)
  - Optimal lag structure (12-month lag strongest absolute Fed Funds relationship)
  - Group sensitivity heterogeneity (Home Price most negative, Gold positive)
  - Outlier concentration in stress periods (notably 2008, plus 2011 and 2020 episodes)
- Added explicit M3 model implications:
  - Driver-effect lag specification
  - Control premium sign expectations
  - Group × driver interaction terms
- Documented data-quality risks and mitigations:
  - Missingness
  - Heteroskedasticity (with robust-SE recommendation)
  - Multicollinearity (with variable-selection/VIF monitoring guidance)


---

## Verification & Modifications (Disclose • Verify • Critique)

### Task 1: Data Collection Scripts

**Verify:**
- All scripts tested and confirmed successful data retrieval
- 14 FRED series fetched with proper date ranges and frequencies
- S&P 500: 6,286 daily observations from 2001-02-26
- Gold: 6,273 daily observations from 2001-02-26 (25 years)
- Bitcoin: 4,179 daily observations from 2014-09-17
- All data saved to correct `data/raw/` locations with proper formatting
- Error handling validated for API failures and missing credentials

**Critique:**
- Initial attempts to fetch gold from FRED failed (series IDs don't exist in FRED)
- First gold API call used GOLD_SILVER_SPOT which only returns current price
- Had to iterate through multiple API response formatters for Alpha Vantage's GOLD_SILVER_HISTORY endpoint
- MetalPriceAPI free tier limitation discovered mid-project (only 30 days of data available)
- Required three different data source attempts (Alpha Vantage → MetalPriceAPI → Yahoo Finance)

**Modify:**
- Switched from FRED gold lookup → Alpha Vantage GOLD_SILVER_HISTORY → MetalPriceAPI → Yahoo Finance (yfinance)
- Consolidated M1/M2 scripts into comprehensive multi-series `fetch_all_fred_economic_data.py`
- Updated `fetch_asset_prices.py` to combine S&P 500, gold, and Bitcoin fetching in one script
- Changed CPI series to MEDCPIM158SFRBCLE per user preference
- Added CSUSHPISA (Case-Shiller Home Price Index)
- Final implementation uses yfinance library with free access (no API key required)

---

### Task 2: Data Cleaning & Merging

**Verify:**
- `create_final_dataset.py` tested on all 17 datasets
- Final merged dataset shape verified: 297 rows × 17 columns
- Date range confirmed: 2001-02-28 to 2025-10-31 (24.7 years)
- All frequency standardizations working correctly (daily→monthly, quarterly→monthly, monthly→month-end)
- Missing value handling verified:
  - 548 yield curve values filled (4.2% of series)
  - 94 BBB spread values filled (1.2% of series)
  - Bitcoin NaN pre-2014 preserved by design (163 months, 54.9% of total)
  - All other variables at 100% completeness after processing
- Processed files saved to `data/processed/`
- Final merged file saved to `data/final/merged_economic_data.csv`

**Critique:**
- Bitcoin completeness at only 45.1% due to asset non-existence pre-2014
- GDP is quarterly data requiring monthly forward-fill (introduces data repetition)
- Some variables have significant missing value gaps that required imputation

**Modify:**
- Decided to retain Bitcoin pre-2014 as NaN (not imputed) to preserve data integrity and disclose asset non-existence
- Used forward/backward fill for market closures only (not for structural gaps)
- Aligned all datasets to gold data start date (2001-02-26) as the earliest common reference point
- Documented all imputation decisions in missing values report

---

### Task 3: Report Generation

**Verify:**
- Data quality report created with comprehensive documentation (476 lines)
- All data sources, frequencies, and coverage documented
- Cleaning decisions explained for each variable
- Merge strategy verified with row/column counts
- Data dictionary created with 17 variable definitions
- All reproducibility steps documented and tested
- Ethical considerations section included

**Modify:**
- Restructured report to clarify Yahoo Finance as PRIMARY (defines date range) and FRED as SUPPLEMENTARY (provides macro context)
- Added detailed missing value handling table
- Created separate concise data dictionary for quick reference
- Updated section headings to clearly denote primary vs. supplementary sources
- Documented Bitcoin NaN retention as ethical decision (transparency > false completeness)

---

### Task 4: EDA Notebook Generation

**Verify:**
- Notebook runs end-to-end with all 8 required figures generated and saved
- Plot captions aligned to interpretation guidance provided during revision process
- Plot 3 visual readability improved (line layering, legend placement)
- Plot 7 includes explicit slope labels in legends
- Plot styling updated to seaborn colorblind-friendly palette and validated on regenerated figures
- Final notebook location verified at `code/capstone_eda.ipynb` (duplicate files removed)

**Critique:**
- Initial notebook iterations had kernel-state dependency issues (cells failed when run out of order)
- Early captions were too generic and required multiple rounds of interpretation-specific refinement
- Some plot legends initially obscured data and needed manual repositioning
- Plot color settings were initially mixed (hard-coded colors + theme defaults) before standardization

**Modify:**
- Added explicit rolling-average overlays and layering controls where needed
- Reworked legends (especially Plot 3 and Plot 7) for clarity and non-overlap
- Added one-sentence context lines before each visualization code block per instructor preference
- Converted manual color assignments to use consistent colorblind-friendly palette references
- Updated decomposition labeling conventions (`divergence_index` -> `Divergence Index`)

---

### Task 5: EDA Summary Generation

**Verify:**
- `M2_EDA_summary.md` created in `results/reports/` with all required rubric sections
- Included 3+ hypotheses with claim, model form, expected sign, and mechanism
- Data-quality section explicitly addresses outliers, missingness, heteroskedasticity, and multicollinearity with planned mitigations

**Critique:**
- Initial draft risked being overly narrative without enough numeric grounding
- Needed explicit connection between EDA findings and concrete M3 specifications

**Modify:**
- Added quantitative support (key correlations, lag profile, sensitivity ranking)
- Tightened hypotheses to map directly into estimable M3 model terms
- Expanded mitigation notes to include robust SEs, interaction terms, and control-set checks


---

## Reflection on AI Use

### What Did AI Help You Learn?

**Task 1 - Data Collection:**
- FRED API (fredapi library) for fetching economic data
- Yahoo Finance API (yfinance) for free historical asset price data
- API error handling and response format parsing
- Environment variable management with `.env` files and security best practices
- Evaluating multiple data sources for reliability, cost, and historical coverage

**Task 2 - Data Cleaning & Merging:**
- Frequency standardization across mixed-frequency time series
- Strategic missing value handling (fill vs. retain based on data source)
- Designing scalable merge pipelines with proper alignment verification
- Documenting data quality decisions for reproducibility and transparency

**Task 3 - Report Generation:**
- Structuring comprehensive technical documentation
- Balancing detail with accessibility (data dictionary vs. extended reports)
- Ethical documentation practices (disclosing exclusions, trade-offs, limitations)

**Task 4 - EDA Notebook Generation:**
- Translating milestone instructions into a full notebook workflow with reproducible figures
- Improving plot communication through iterative legend, caption, and layering revisions
- Applying accessible visualization practices (colorblind-safe palettes, clearer labels)

**Task 5 - EDA Summary Generation:**
- Converting descriptive EDA outputs into testable econometric hypotheses
- Linking diagnostics (lags, heterogeneity, multicollinearity, heteroskedasticity) to model-design decisions
- Writing concise evidence-to-model narratives for milestone reporting

### What Did AI Get Wrong or Require Correction?

**Task 1:**
- Initial attempts to fetch gold from FRED with non-existent series IDs (GOLDPMGBD228NLBM, GOLDAMGBD228NLBM, GOLDS)
- GOLD_SILVER_SPOT endpoint only returns current price, not historical data
- Multiple API response format iterations needed for Alpha Vantage's GOLD_SILVER_HISTORY endpoint
- MetalPriceAPI suggested without checking free tier limitations (only 30 days available)
- Required 3 different data sources (Alpha Vantage → MetalPriceAPI → Yahoo Finance) before optimal solution

**Task 2:**
- Initial imputation approach of filling all missing values (corrected to preserve Bitcoin NaN for transparency)
- Did not initially account for quarterly-to-monthly conversion implications (data repetition)

**Task 3:**
- Section structure needed reordering to clarify primary (Yahoo Finance) vs. supplementary (FRED) data hierarchy
- Initial report lacked explicit ethical considerations section (added post-draft)

**Task 4:**
- Initial notebook version required troubleshooting for execution state/order
- Some default legend placements blocked important lines and had to be manually moved
- Early caption drafts were too generic and needed revisions tied to actual plotted patterns
- Plot colors required explicit standardization to fully align with colorblind-friendly guidance

**Task 5:**
- First-pass summary language was too broad; required stronger numeric anchoring and tighter hypothesis structure
- Needed explicit mapping from EDA diagnostics to concrete M3 mitigation steps

---

# Milestone 3 Update: Econometric Models (April 2026)

## Tool(s) Used
- GitHub Copilot (GPT-5.3-Codex)

## Task(s) Where AI Was Used (M3)
1. **Task M3-1:** Implement `code/capstone_models.py` with required sectioned structure.
2. **Task M3-2:** Implement Model A (Fixed Effects panel model) with entity and time effects.
3. **Task M3-3:** Implement Model B (Machine Learning comparison: Random Forest vs OLS).
4. **Task M3-4:** Implement required diagnostics (Breusch-Pagan, VIF, residual diagnostics).
5. **Task M3-5:** Implement robustness checks (robust SE, alternative lags, placebo lead test).
6. **Task M3-6:** Save publication-ready output tables and figures to milestone-required folders.
7. **Task M3-7:** Update dependency file for reproducibility.
8. **Task M3-8:** Draft `M3_interpretation.md` with economic interpretation, diagnostics interpretation, robustness summary, and caveats.

## Key Prompts (M3)
1. "Start Milestone 3 from the existing project context and keep consistency with M2 definitions."
2. "Create `capstone_models.py` that runs top-to-bottom with relative paths and section headers."
3. "Model A must be Fixed Effects and include diagnostics and robustness checks."
4. "Choose one Model B option; implement ML comparison and save performance tables/plots."
5. "Update AI audit appendix for this milestone and double-check consistency/accuracy."

## Output Summary (M3)

### 1) Script Created
- `code/capstone_models.py` added with full M3 structure:
  - Section 1: Imports/data loading (`merged_analysis_panel.csv`)
  - Section 2: Feature engineering and panel reshape
  - Section 3: Model A Fixed Effects estimation
  - Section 4: Model B ML comparison (RF vs OLS)
  - Section 5: Diagnostics
  - Section 6: Robustness checks
  - Section 7: Saved outputs

### 2) Model A (Required Fixed Effects)
- Built an asset-level panel (`asset` × `date`) from M2-consistent monthly returns:
  - `ret_SP500`, `ret_HomePrice`, `ret_Gold`
- Included entity and time effects in `PanelOLS` when available.
- Used exposure-based policy interaction term to maintain identification with time FE in a macro-shock panel context.
- Produced clustered and robust standard-error variants.

### 3) Model B (Chosen Option: ML comparison)
- Implemented train/test comparison:
  - OLS benchmark (`LinearRegression`)
  - `RandomForestRegressor`
- Reported test-set `R^2` and RMSE.
- Exported RF feature importance table and figure.

### 4) Diagnostics Implemented
- Breusch-Pagan heteroskedasticity test output.
- VIF table for predictor multicollinearity.
- Residual diagnostics plots:
  - Residuals vs fitted
  - Q-Q plot

### 5) Robustness Checks Implemented
- Alternative policy lags (`lag12`, `lag6`, `lag3`).
- Placebo lead test (`lead12`).
- Outlier exclusion re-estimation (2008-2009 crisis window and Mar-May 2020).
- Group subsample re-estimation by asset class (S&P 500, Home Price, Gold).
- Exported coefficient and p-value table by specification.

### 6) Output Locations
- Tables written to `results/tables/`.
- Figures written to `results/figures/`.
- Run summary text file generated for quick audit trail.

### 7) Reproducibility Update
- Updated `technicals/requirements.txt` to include:
  - `numpy`, `seaborn`, `statsmodels`, `linearmodels`, `scikit-learn`

## Verification & Modifications (Disclose • Verify • Critique)

### Verify
- Confirmed script uses relative path imports via `config_paths` constants (`FINAL_DATA_DIR`, `FIGURES_DIR`, `TABLES_DIR`).
- Confirmed sectioned structure aligns with Milestone 3 rubric requirements.
- Confirmed M2-consistent outcome engineering pipeline (asset returns and divergence construction logic retained as reference context).
- Confirmed all required output artifacts are explicitly saved to required directories.

### Critique
- Current container environment did not include all runtime packages by default, so full end-to-end execution could not be validated here without environment setup.
- Panel identification with two-way FE in a macro-only shock setup requires interaction-based terms; direct common macro levels are absorbed by time effects.

### Modify
- Added fallback path to OLS with entity/time dummies if `linearmodels` is unavailable.
- Added explicit comments documenting identification choice and fallback behavior.
- Added standardized output exports for tables/figures to support publication-ready reporting workflow.

## Reflection on AI Use (M3)
- AI accelerated implementation of a reproducible M3 script architecture and standardized output pipeline.
- AI assisted in translating M2 findings into estimable model terms (lag choice, panel reshape, diagnostics, robustness).
- Human oversight remained necessary for dataset-specific identification decisions and consistency checks with prior milestone definitions.
