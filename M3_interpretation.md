# M3 Interpretation Memo

## Model A Headline
A 1-unit increase in the 12-month lagged policy exposure term is associated with a -0.0029 percentage-point change in monthly asset return (p-value = 0.6679) in the two-way fixed effects specification.

## Economic Interpretation
- Channel 1 (discount-rate sensitivity): assets with higher rate exposure can reprice through financing and discount-rate channels after policy changes.
- Channel 2 (risk sentiment): VIX-related exposure captures changes in risk appetite that shift performance asymmetrically across asset classes.
- Channel 3 (momentum/mean reversion): lagged return and 3-month momentum terms show strong dynamics, indicating persistence and subsequent correction effects in returns.

## Model B Summary (ML vs OLS)
- OLS test R2: 0.4454; test RMSE: 2.6180
- Random Forest test R2: 0.4969; test RMSE: 2.4934
- Key takeaway: Random Forest provides higher predictive fit and lower forecast error, but OLS/FE remains more interpretable for causal discussion.

## Diagnostics
- Breusch-Pagan LM p-value = 0.000421. Since p < 0.05, heteroskedasticity is present.
- VIF max = 1.8287 (below 10 threshold), suggesting no severe multicollinearity problem in selected predictors.
- Residual diagnostics were saved to figures and inspected via residuals-vs-fitted and Q-Q plots.

## Robustness Checks
- Robust vs clustered SE comparison reported in table.
- Alternative lag specifications tested (lag 3, 6, 12).
- Placebo lead test estimated.
- Outlier exclusion estimated (2008-2009 crisis and Mar-May 2020).
- Group subsamples estimated by asset class (SP500, HomePrice, Gold).

## Caveats
- Omitted-variable risk remains for unobserved time-varying drivers not captured by included controls.
- Time FE absorb common macro shocks, so policy interpretation relies on cross-asset exposure variation.
- External validity is limited to this asset mix, frequency, and sample window.

## Files Produced
- Tables: results/tables/M3_*.csv
- Figures: results/figures/M3_*.png
