# M3 Interpretation Memo

## Model A Headline
A 1-unit increase in the 12-month lagged policy exposure term is associated with a -0.0029 percentage-point change in monthly asset return (p-value = 0.6679) in the two-way fixed effects specification.

- Statistical interpretation: with p-value > 0.10, we fail to reject the null that the average policy-exposure effect is zero in this specification.
- Practical interpretation: the point estimate is economically small relative to typical month-to-month return volatility, so effect size appears limited in-sample.

## Economic Interpretation
- Channel 1 (discount-rate sensitivity): assets with higher rate exposure can reprice through financing and discount-rate channels after policy changes.
- Channel 2 (risk sentiment): VIX-related exposure captures changes in risk appetite that shift performance asymmetrically across asset classes.
- Channel 3 (momentum/mean reversion): lagged return and 3-month momentum terms show strong dynamics, indicating persistence and subsequent correction effects in returns.
- Combined read: policy signals appear to operate through interaction terms and dynamics rather than as a large direct average shift in returns.
- Estimated risk channel magnitude: the VIX exposure coefficient is -0.0040, which is consistent with higher uncertainty being associated with weaker risk-asset performance after conditioning on FE.
- Dynamic adjustment pattern: Return Lag 1 (-0.5009) and Return Momentum (3M) (1.5032) point to short-horizon reversal plus medium-horizon continuation, suggesting partial overshooting followed by correction.
- Asset-class implication: because policy and VIX effects enter through exposure interactions, transmission is heterogeneous by asset type rather than uniform across all markets in a given month.
- Portfolio interpretation: the results are more consistent with relative-rotation effects (winners vs. losers across assets) than with a single common directional response to policy changes.

## Model B Summary (ML vs OLS)
- OLS test R2: 0.4454; test RMSE: 2.6180
- Random Forest test R2: 0.4969; test RMSE: 2.4934
- Key takeaway: Random Forest provides higher predictive fit and lower forecast error, but OLS/FE remains more interpretable for causal discussion.
- Model-use guidance: use FE/OLS outputs for coefficient interpretation and policy discussion; use Random Forest for forecast-oriented benchmarking.

## Diagnostics
- Breusch-Pagan LM p-value = 0.000421. Since p < 0.05, heteroskedasticity is present.
- VIF max = 1.8287 (below 10 threshold), suggesting no severe multicollinearity problem in selected predictors.
- Residual diagnostics were saved to figures and inspected via residuals-vs-fitted and Q-Q plots.
- Implication: heteroskedasticity supports reporting robust/clustered standard errors as the primary inferential basis.

## Robustness Checks
- Standard vs clustered vs HC-robust SE comparison reported in table.
- Alternative lag specifications tested (lag 3, 6, 12).
- Placebo lead test estimated.
- Outlier exclusion estimated (2008-2009 crisis and Mar-May 2020).
- Group subsamples estimated by asset class (SP500, HomePrice, Gold).
- HC covariance estimator robustness check (HC0, HC1, HC2, HC3): coefficient and standard error comparisons show stability across specifications.
- HC covariance estimator SEs range from 0.0763 to 0.0763 across HC0-HC3, indicating robustness to HC specification choice.
- Bottom line: qualitative conclusions are stable across timing assumptions, crisis-window exclusions, and standard error estimators.

## Caveats
- Omitted-variable risk remains for unobserved time-varying drivers not captured by included controls.
- Time FE absorb common macro shocks, so policy interpretation relies on cross-asset exposure variation.
- External validity is limited to this asset mix, frequency, and sample window.
- Potential extension: add alternative macro controls (e.g., liquidity proxies) and perform rolling-window estimation to test temporal stability.

## Files Produced
### Report
- Narrative findings: M3_interpretation.md

### Tables
- Full FE outputs: results/tables/M3_modelA_regression_table.csv
- Publication table: results/tables/M3_regression_table.csv
- Heteroskedasticity test: results/tables/M3_modelA_breusch_pagan.csv
- Multicollinearity check: results/tables/M3_modelA_vif.csv
- Robustness specs: results/tables/M3_modelA_robustness_checks.csv
- ML vs OLS: results/tables/M3_modelB_ml_comparison.csv
- Feature ranks: results/tables/M3_modelB_rf_feature_importance.csv
- Run inventory: results/tables/M3_run_summary.txt

### Figures
- Residual pattern: results/figures/M3_residuals_vs_fitted.png
- Normality check: results/figures/M3_qq_plot.png
- HC SE comparison: results/figures/M3_modelA_robust_se_comparison.png
- Top predictors: results/figures/M3_modelB_rf_feature_importance_top10.png
