# M2 EDA Summary

## Key Findings

- **Uncertainty is the strongest control correlate of divergence**: Divergence has its largest absolute bivariate relationship with VIX ($r=0.55$), consistent with a risk-off mechanism in which broad uncertainty increases cross-asset return dispersion.
- **Credit stress and sentiment also carry meaningful signal**: BBB spread is positively related to divergence ($r=0.48$) and consumer sentiment is negatively related ($r=-0.31$), matching a financing-risk channel (wider spreads) and confidence channel (higher sentiment compresses dispersion).
- **Optimal policy lag is 12 months, not contemporaneous**: Lagged Fed Funds correlations transition from weakly negative at short horizons ($r_{0}=-0.108$, $r_{1}=-0.090$) to near zero at 6 months ($r_{6}=-0.001$), then positive at 12 months ($r_{12}=0.111$, strongest absolute value). This pattern is consistent with delayed transmission via refinancing, balance-sheet adjustment, and portfolio reallocation.
- **Rate sensitivity differs by asset group (heterogeneous slope evidence)**: Home Price Index is most negatively sensitive to Fed Funds ($r=-0.165$), S&P 500 is near zero ($r=-0.008$), and Gold is positive ($r=0.127$), suggesting financing-cost exposure for housing, mixed offsetting channels for equities, and inflation/hedging demand dynamics for gold.
- **Outlier episodes cluster in stress windows**: Highest divergence months are concentrated in 2008 (Oct/Nov peaks), with additional spikes in 2011 and 2020. This supports a crisis-regime mechanism where shocks temporarily widen cross-asset performance gaps.

## Hypotheses for M3

### Hypothesis 1 (Driver Effect: Policy Rate)
- **Claim**: The effect of policy rates on divergence is lagged and state-dependent rather than purely contemporaneous.
- **Model specification**:  
  $$\text{Divergence}_t = \alpha + \beta_0 \text{FFR}_t + \beta_{12}\text{FFR}_{t-12} + \gamma'\mathbf{X}_t + \varepsilon_t$$
- **Expected sign**: $\beta_0 \le 0$ (short run weakly negative), $\beta_{12} > 0$ (12-month delayed positive association).
- **Mechanism**: Immediate policy changes can compress risk-taking in the short run, while delayed refinancing, maturity rollover, and portfolio reweighting can amplify divergence later.

### Hypothesis 2 (Control Premiums: Risk and Confidence)
- **Claim**: Uncertainty and credit stress widen divergence; confidence narrows it.
- **Model specification**: Add controls $\text{VIX}_t$, $\text{BBBSpread}_t$, $\text{Sentiment}_t$, and optionally $\text{EPU}_t$ to baseline M3.
- **Expected sign**: $\beta_{VIX}>0$, $\beta_{BBB}>0$, $\beta_{Sentiment}<0$, $\beta_{EPU}>0$.
- **Mechanism**: Risk-off episodes and tighter financial conditions create uneven repricing across asset classes, while stronger confidence aligns expected returns and compresses dispersion.

### Hypothesis 3 (Group Heterogeneity)
- **Claim**: Policy-rate effects are heterogeneous across asset classes.
- **Model specification**:  
  $$\text{Return}_{g,t}=\alpha_g + \beta\text{FFR}_t + \sum_g \delta_g(\text{Group}_g \times \text{FFR}_t) + \theta'\mathbf{X}_t + u_{g,t}$$
- **Expected sign**: More negative interaction for Home Price group, near-zero for S&P 500, and less negative/positive for Gold.
- **Mechanism**: Housing is more financing-cost sensitive, equities reflect mixed discount-rate vs earnings channels, and gold behaves more as an inflation/uncertainty hedge.

## Data Quality Flags and M3 Mitigations

- **Outlier periods**: Major divergence outliers occur in crisis months (notably 2008, plus 2011 and 2020 episodes).  
  **Mitigation**: Include crisis/regime indicators and run robustness checks (winsorized outcome, robust regressions).
- **Missing values**: Minimal missingness in core modeling columns (0% for most controls; ~0.34% in divergence and M2 growth from first-difference construction).  
  **Mitigation**: Use complete-case estimation after lag/difference transforms and report effective sample size by specification.
- **Heteroskedasticity risk**: Volatility clustering in plots and Breusch-Pagan test significance (LM/F p-values ~0.038) indicate non-constant residual variance.  
  **Mitigation**: Use heteroskedasticity-robust (HC) standard errors; consider regime interactions if residual variance remains state-dependent.
- **Multicollinearity risk**: High co-movement among rate-term controls (e.g., Fed Funds and Real 10Y relationship; top VIFs: Fed Funds ~9.97, Real 10Y ~5.47, Yield Curve ~5.20).  
  **Mitigation**: Avoid redundant rate controls in the same specification, compare alternative control sets, and monitor VIF/standard-error inflation in final M3 models.

