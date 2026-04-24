# AI Audit Appendix (Assignment 05)

## Tool(s) Used
- GitHub Copilot (Claude Haiku 4.5 for earlier tasks; GPT-5.3-Codex for Milestone 3 updates)

## Task(s) Where AI Was Used
1. **Task 1:** Data Collection — Fetching economic data from FRED API and asset prices from Yahoo Finance
2. **Task 2:** Data Cleaning & Merging — Creating consolidated dataset with standardized frequency and alignment
3. **Task 3:** Report Generation — Creating data quality documentation and data dictionary
4. **Task 4:** EDA Notebook Generation — Building and iteratively refining `capstone_eda.ipynb` with 8 required M2 visualizations
5. **Task 5:** Model Script Generation — Creating and refining `code/capstone_models.py` for Milestone 3 models, diagnostics, robustness checks, and output exports
6. **Task 6:** M3 Interpretation Generation — Creating and iteratively improving `M3_interpretation.md` with model interpretation, diagnostics, robustness summary, and finalized files-produced documentation

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

### Task 5: Model Script Generation
1. "create the M3 models script with fixed effects model + random forest comparison"
3. "add a robust standard error robustness check to the models script. update tables/figures/report as needed"
4. "Please update the tables and figures to not have _ where not needed"

### Task 6: M3 Interpretation Generation
1. "Please add some more detail to the report. definitely update the files produced section. format it a little cleaner (keep the sections as is)"
2. "write a super short explanation of what each item is in the files produced section"
3. "keep them seperated by type and maybe add the description before or after-- its not super noticable"


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

### Task 5: Model Script Generation

**Created `code/capstone_models.py` to satisfy M3 modeling requirements:**
- Implemented Model A (two-way fixed effects panel specification with entity and time effects)
- Implemented Model B (Random Forest vs OLS comparison with test R2 and RMSE)
- Added required diagnostics:
  - Breusch-Pagan heteroskedasticity test
  - VIF multicollinearity checks
  - Residual-vs-fitted and Q-Q diagnostic plots
- Added robustness checks:
  - Alternative lag specifications (lag 3/6/12)
  - Placebo lead test
  - Crisis-window exclusion re-estimation
  - Asset-group subsample tests
  - Robust SE covariance comparison (HC0/HC1/HC2/HC3)
- Exported milestone outputs to required folders (`results/tables/`, `results/figures/`)
- Cleaned output labels to publication-friendly naming (removed unnecessary underscores in table columns and feature names)

### Task 6: M3 Interpretation Generation

**Created and iteratively refined `M3_interpretation.md`:**
- Preserved required section structure while expanding interpretation detail
- Added stronger model-read guidance:
  - Statistical interpretation of the policy effect estimate
  - Practical/economic magnitude interpretation
  - FE/OLS vs Random Forest usage guidance
- Expanded diagnostics and robustness narrative with concise takeaways
- Reworked `Files Produced` section for readability:
  - Separated by type (`Report`, `Tables`, `Figures`)
  - Added ultra-short per-item descriptions
  - Improved scanability/format clarity while keeping section headings intact


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

### Task 5: Model Script Generation

**Verify:**
- `code/capstone_models.py` executes end-to-end and writes all M3 artifacts to `results/tables/` and `results/figures/`
- Model A and Model B outputs generated successfully with diagnostics and robustness tables
- Robust SE comparison entries present in `M3_modelA_robustness_checks.csv`
- RF feature-importance outputs generated as both table and figure

**Critique:**
- Initial outputs used overly technical/underscored labels that were less publication-friendly
- Robust-SE robustness reporting needed clearer explicit comparison entries

**Modify:**
- Added robust covariance comparison rows (HC0/HC1/HC2/HC3) into robustness output
- Added robust SE comparison figure for quick visual inspection
- Refactored output label formatting for cleaner column names and feature labels

### Task 6: M3 Interpretation Generation

**Verify:**
- `M3_interpretation.md` generated successfully from script and aligned with M3 outputs
- All required sections retained and expanded with additional interpretive detail
- `Files Produced` section updated to explicit, readable artifact inventory

**Critique:**
- Initial memo draft was too concise in headline interpretation and practical implications
- Files list was initially generic and harder to scan quickly

**Modify:**
- Added short, high-signal interpretation bullets in Model A/Model B/Diagnostics sections
- Reorganized file inventory by output type and added brief per-item explanations
- Tightened formatting for cleaner section flow without changing required headings


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

**Task 5 - Model Script Generation:**
- Structuring an end-to-end econometric modeling pipeline with reproducible exports
- Implementing FE + ML comparison workflows with diagnostics and robustness checks
- Converting technical variable names into publication-ready output labeling

**Task 6 - M3 Interpretation Generation:**
- Writing concise model interpretation with both statistical and practical framing
- Organizing artifact inventories for readability and auditability
- Iteratively improving technical prose while preserving required section structure

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
- Initial model output labels were too technical for report-facing tables and figure readability
- Robustness checks initially needed explicit robust-SE comparison entries to be clearer for interpretation

**Task 6:**
- First interpretation draft was too terse and required more practical context around coefficient meaning
- Files-produced list was initially present but not visually prominent enough for quick grading/audit
