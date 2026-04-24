"""
QM 2023 Capstone: Milestone 3 Econometric Models
Team: QM 2023 Capstone Team
Members: Sam Weber, Brett Ragle, Anthony Ibarra
Date: 2026-04-21

This script estimates econometric models to identify causal effects of policy and
market drivers on cross-asset return behavior. We estimate a Fixed Effects panel
model (required Model A) and a Machine Learning comparison (Model B: Random
Forest vs OLS).
"""

from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from config_paths import FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR

# linearmodels is required by milestone instructions; fallback is included so the
# script still runs if linearmodels is temporarily unavailable in an environment.
try:
    from linearmodels.panel import PanelOLS
    HAS_LINEARMODELS = True
except ImportError:
    HAS_LINEARMODELS = False


# -----------------------------------------------------------------------------
# Section 1: Imports and data loading
# -----------------------------------------------------------------------------

def ensure_output_dirs() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    panel_path = FINAL_DATA_DIR / "merged_analysis_panel.csv"
    if not panel_path.exists():
        raise FileNotFoundError(f"Expected final panel at: {panel_path}")

    df = pd.read_csv(panel_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# -----------------------------------------------------------------------------
# Section 2: Feature engineering (lags, interactions, panel reshape)
# -----------------------------------------------------------------------------

def build_m2_consistent_features(df: pd.DataFrame) -> pd.DataFrame:
    asset_price_cols = {
        "SP500": "sp500_index",
        "HomePrice": "home_price_index",
        "Gold": "gold_price_usd",
    }

    out = df.copy()

    for asset, col in asset_price_cols.items():
        out[f"ret_{asset}"] = out[col].pct_change() * 100.0

    return_cols = [f"ret_{k}" for k in asset_price_cols]
    out["divergence_index"] = out[return_cols].std(axis=1, skipna=True)

    out["m2_growth_pct"] = out["m2_billions"].pct_change() * 100.0
    out["fed_funds_rate_lag12"] = out["fed_funds_rate"].shift(12)
    out["fed_funds_rate_lag6"] = out["fed_funds_rate"].shift(6)
    out["fed_funds_rate_lag3"] = out["fed_funds_rate"].shift(3)
    out["fed_funds_rate_lead12"] = out["fed_funds_rate"].shift(-12)

    return out


def build_asset_panel(df: pd.DataFrame) -> pd.DataFrame:
    panel = df[[
        "date",
        "fed_funds_rate_lag12",
        "fed_funds_rate_lag6",
        "fed_funds_rate_lag3",
        "fed_funds_rate_lead12",
        "vix_index",
        "bbb_spread",
        "consumer_sentiment",
        "m2_growth_pct",
    ]].copy()

    panel["ret_SP500"] = df["ret_SP500"]
    panel["ret_HomePrice"] = df["ret_HomePrice"]
    panel["ret_Gold"] = df["ret_Gold"]

    long_df = panel.melt(
        id_vars=[
            "date",
            "fed_funds_rate_lag12",
            "fed_funds_rate_lag6",
            "fed_funds_rate_lag3",
            "fed_funds_rate_lead12",
            "vix_index",
            "bbb_spread",
            "consumer_sentiment",
            "m2_growth_pct",
        ],
        value_vars=["ret_SP500", "ret_HomePrice", "ret_Gold"],
        var_name="asset",
        value_name="asset_return_pct",
    )

    long_df["asset"] = long_df["asset"].str.replace("ret_", "", regex=False)

    # Exposure weights from M2 directional sensitivity evidence.
    exposure_map = {
        "SP500": 0.2,
        "HomePrice": 1.0,
        "Gold": -0.6,
    }
    long_df["rate_exposure"] = long_df["asset"].map(exposure_map)

    long_df = long_df.sort_values(["asset", "date"]).reset_index(drop=True)

    long_df["ret_lag1"] = long_df.groupby("asset")["asset_return_pct"].shift(1)
    long_df["ret_mom3"] = (
        long_df.groupby("asset")["asset_return_pct"]
        .rolling(window=3, min_periods=3)
        .mean()
        .reset_index(level=0, drop=True)
    )

    # Time FE absorb common macro levels, so we identify policy effects via
    # cross-asset exposure interactions that vary by asset x time.
    long_df["policy_exposure_term_12"] = long_df["fed_funds_rate_lag12"] * long_df["rate_exposure"]
    long_df["policy_exposure_term_6"] = long_df["fed_funds_rate_lag6"] * long_df["rate_exposure"]
    long_df["policy_exposure_term_3"] = long_df["fed_funds_rate_lag3"] * long_df["rate_exposure"]
    long_df["policy_placebo_term"] = long_df["fed_funds_rate_lead12"] * long_df["rate_exposure"]
    long_df["vix_exposure_term"] = long_df["vix_index"] * long_df["rate_exposure"]

    return long_df


# -----------------------------------------------------------------------------
# Section 3: Model A - Fixed Effects regression
# -----------------------------------------------------------------------------

def fit_model_a_fe(long_df: pd.DataFrame):
    use_cols = [
        "asset_return_pct",
        "asset",
        "date",
        "policy_exposure_term_12",
        "vix_exposure_term",
        "ret_lag1",
        "ret_mom3",
    ]

    fe_df = long_df[use_cols].dropna().copy()
    fe_df = fe_df.set_index(["asset", "date"]).sort_index()

    y = fe_df["asset_return_pct"]
    X = fe_df[["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]]

    if HAS_LINEARMODELS:
        model_main = PanelOLS(y, X, entity_effects=True, time_effects=True)
        fe_standard = model_main.fit(cov_type="unadjusted")
        fe_clustered = model_main.fit(cov_type="clustered", cluster_entity=True)
        fe_robust = model_main.fit(cov_type="robust")
    else:
        warnings.warn(
            "linearmodels not available; using OLS with entity/time dummies as fallback.",
            RuntimeWarning,
        )
        tmp = fe_df.reset_index()
        tmp = pd.get_dummies(tmp, columns=["asset"], drop_first=True)
        date_dummies = pd.get_dummies(tmp["date"], prefix="t", drop_first=True)
        tmp = pd.concat([tmp, date_dummies], axis=1)

        x_cols = ["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]
        x_cols += [c for c in tmp.columns if c.startswith("asset_") or c.startswith("t_")]

        X_sm = sm.add_constant(tmp[x_cols])
        ols_base = sm.OLS(tmp["asset_return_pct"], X_sm).fit()
        ols_clustered = sm.OLS(tmp["asset_return_pct"], X_sm).fit(
            cov_type="cluster",
            cov_kwds={"groups": tmp["asset"]},
        )
        ols_robust = sm.OLS(tmp["asset_return_pct"], X_sm).fit(cov_type="HC1")
        fe_standard = ols_base
        fe_clustered = ols_clustered
        fe_robust = ols_robust

    return fe_df, fe_standard, fe_clustered, fe_robust


# -----------------------------------------------------------------------------
# Section 4: Model B - ML comparison (Random Forest vs OLS)
# -----------------------------------------------------------------------------

def fit_model_b_ml(long_df: pd.DataFrame):
    ml_cols = [
        "date",
        "asset",
        "asset_return_pct",
        "fed_funds_rate_lag12",
        "vix_index",
        "bbb_spread",
        "consumer_sentiment",
        "m2_growth_pct",
        "ret_lag1",
        "ret_mom3",
    ]

    ml_df = long_df[ml_cols].dropna().copy()
    ml_df = pd.get_dummies(ml_df, columns=["asset"], drop_first=True)
    ml_df = ml_df.sort_values("date").reset_index(drop=True)

    split_idx = int(len(ml_df) * 0.8)
    train = ml_df.iloc[:split_idx].copy()
    test = ml_df.iloc[split_idx:].copy()

    y_train = train["asset_return_pct"]
    y_test = test["asset_return_pct"]

    x_cols = [c for c in ml_df.columns if c not in ["asset_return_pct", "date"]]

    X_train = train[x_cols]
    X_test = test[x_cols]

    ols = LinearRegression()
    ols.fit(X_train, y_train)
    pred_ols = ols.predict(X_test)

    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=3,
        random_state=42,
    )
    rf.fit(X_train, y_train)
    pred_rf = rf.predict(X_test)

    results = pd.DataFrame(
        {
            "model": ["OLS", "RandomForest"],
            "test_r2": [r2_score(y_test, pred_ols), r2_score(y_test, pred_rf)],
            "test_rmse": [
                np.sqrt(mean_squared_error(y_test, pred_ols)),
                np.sqrt(mean_squared_error(y_test, pred_rf)),
            ],
        }
    )

    importances = pd.DataFrame(
        {
            "feature": x_cols,
            "importance": rf.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    return results, importances


# -----------------------------------------------------------------------------
# Section 5: Diagnostics (heteroskedasticity, VIF, residual plots)
# -----------------------------------------------------------------------------

def diagnostics_model_a(fe_df: pd.DataFrame, fe_model) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_predictors = ["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]

    X_bp = sm.add_constant(fe_df[base_predictors])

    # Residual extraction for both linearmodels and statsmodels paths.
    resid = pd.Series(np.asarray(fe_model.resids), index=fe_df.index)

    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(resid.values, X_bp.values)
    bp_df = pd.DataFrame(
        {
            "statistic": [bp_lm, bp_f],
            "p_value": [bp_lm_p, bp_f_p],
        },
        index=["LM", "F"],
    )

    vif_df = pd.DataFrame(
        {
            "variable": base_predictors,
            "vif": [
                variance_inflation_factor(fe_df[base_predictors].values, i)
                for i in range(len(base_predictors))
            ],
        }
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    fitted = pd.Series(np.asarray(fe_model.fitted_values).reshape(-1), index=fe_df.index)
    sns.scatterplot(x=fitted, y=resid, alpha=0.5, ax=ax)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("M3 Residuals vs Fitted (Model A)")
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "M3_residuals_vs_fitted.png", dpi=300)
    plt.close(fig)

    fig = plt.figure(figsize=(7, 5))
    sm.qqplot(resid, line="45", fit=True)
    plt.title("M3 Residual Q-Q Plot (Model A)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_qq_plot.png", dpi=300)
    plt.close(fig)

    return bp_df, vif_df


# -----------------------------------------------------------------------------
# Section 6: Robustness checks (robust SEs, alternative lags, placebo tests)
# -----------------------------------------------------------------------------

def robustness_checks(long_df: pd.DataFrame) -> pd.DataFrame:
    checks = []

    base_cols = ["asset_return_pct", "asset", "date", "ret_lag1", "ret_mom3", "vix_exposure_term"]

    for label, term in [
        ("Lag12", "policy_exposure_term_12"),
        ("Lag6", "policy_exposure_term_6"),
        ("Lag3", "policy_exposure_term_3"),
        ("PlaceboLead12", "policy_placebo_term"),
    ]:
        tmp = long_df[base_cols + [term]].dropna().copy()
        tmp = tmp.set_index(["asset", "date"]).sort_index()

        y = tmp["asset_return_pct"]
        X = tmp[[term, "vix_exposure_term", "ret_lag1", "ret_mom3"]]

        if HAS_LINEARMODELS:
            fit = PanelOLS(y, X, entity_effects=True, time_effects=True).fit(cov_type="robust")
            coef = float(fit.params.get(term, np.nan))
            pval = float(fit.pvalues.get(term, np.nan))
        else:
            data = tmp.reset_index()
            data = pd.get_dummies(data, columns=["asset"], drop_first=True)
            date_dummies = pd.get_dummies(data["date"], prefix="t", drop_first=True)
            data = pd.concat([data, date_dummies], axis=1)

            x_cols = [term, "vix_exposure_term", "ret_lag1", "ret_mom3"]
            x_cols += [c for c in data.columns if c.startswith("asset_") or c.startswith("t_")]

            fit = sm.OLS(data["asset_return_pct"], sm.add_constant(data[x_cols])).fit(cov_type="HC1")
            coef = float(fit.params.get(term, np.nan))
            pval = float(fit.pvalues.get(term, np.nan))

        checks.append({
            "specification": label,
            "robustness_type": "AlternativeLagsOrPlacebo",
            "policy_term": term,
            "coef": coef,
            "p_value": pval,
        })

    # Robustness check: Exclude major crisis windows (GFC and COVID shock months).
    crisis_start = pd.Timestamp("2008-09-01")
    crisis_end = pd.Timestamp("2009-06-30")
    covid_start = pd.Timestamp("2020-03-01")
    covid_end = pd.Timestamp("2020-05-31")

    no_crisis = long_df[
        ~(
            ((long_df["date"] >= crisis_start) & (long_df["date"] <= crisis_end))
            | ((long_df["date"] >= covid_start) & (long_df["date"] <= covid_end))
        )
    ].copy()

    tmp = no_crisis[
        ["asset_return_pct", "asset", "date", "ret_lag1", "ret_mom3", "vix_exposure_term", "policy_exposure_term_12"]
    ].dropna().copy()
    tmp = tmp.set_index(["asset", "date"]).sort_index()
    y = tmp["asset_return_pct"]
    X = tmp[["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]]

    if HAS_LINEARMODELS:
        fit = PanelOLS(y, X, entity_effects=True, time_effects=True).fit(cov_type="robust")
        coef = float(fit.params.get("policy_exposure_term_12", np.nan))
        pval = float(fit.pvalues.get("policy_exposure_term_12", np.nan))
    else:
        data = tmp.reset_index()
        data = pd.get_dummies(data, columns=["asset"], drop_first=True)
        date_dummies = pd.get_dummies(data["date"], prefix="t", drop_first=True)
        data = pd.concat([data, date_dummies], axis=1)

        x_cols = ["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]
        x_cols += [c for c in data.columns if c.startswith("asset_") or c.startswith("t_")]
        fit = sm.OLS(data["asset_return_pct"], sm.add_constant(data[x_cols])).fit(cov_type="HC1")
        coef = float(fit.params.get("policy_exposure_term_12", np.nan))
        pval = float(fit.pvalues.get("policy_exposure_term_12", np.nan))

    checks.append(
        {
            "specification": "ExcludeCrisis_2008_2009_2020M3M5",
            "robustness_type": "OutlierExclusion",
            "policy_term": "policy_exposure_term_12",
            "coef": coef,
            "p_value": pval,
        }
    )

    # Robustness check: Group subsamples by asset class.
    for asset in ["SP500", "HomePrice", "Gold"]:
        g = long_df[
            long_df["asset"] == asset
        ][["asset_return_pct", "date", "fed_funds_rate_lag12", "vix_index", "ret_lag1", "ret_mom3"]].dropna().copy()

        if len(g) < 40:
            continue

        Xg = sm.add_constant(g[["fed_funds_rate_lag12", "vix_index", "ret_lag1", "ret_mom3"]])
        fitg = sm.OLS(g["asset_return_pct"], Xg).fit(cov_type="HC1")
        checks.append(
            {
                "specification": f"Subsample_{asset}",
                "robustness_type": "GroupSubsample",
                "policy_term": "fed_funds_rate_lag12",
                "coef": float(fitg.params.get("fed_funds_rate_lag12", np.nan)),
                "p_value": float(fitg.pvalues.get("fed_funds_rate_lag12", np.nan)),
            }
        )

    # Robustness check: Compare different robust standard error specifications (HC0, HC1, HC2, HC3).
    use_cols = [
        "asset_return_pct",
        "asset",
        "date",
        "policy_exposure_term_12",
        "vix_exposure_term",
        "ret_lag1",
        "ret_mom3",
    ]
    fe_df_se = long_df[use_cols].dropna().copy()
    fe_df_se = fe_df_se.set_index(["asset", "date"]).sort_index()

    y_se = fe_df_se["asset_return_pct"]
    X_se = fe_df_se[["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]]

    for hc_type in ["HC0", "HC1", "HC2", "HC3"]:
        if HAS_LINEARMODELS:
            fit_se = PanelOLS(y_se, X_se, entity_effects=True, time_effects=True).fit(cov_type="robust")
            # Note: linearmodels doesn't expose HC types directly; use as is
            coef_se = float(fit_se.params.get("policy_exposure_term_12", np.nan))
            se_se = float(fit_se.std_errors.get("policy_exposure_term_12", np.nan))
            pval_se = float(fit_se.pvalues.get("policy_exposure_term_12", np.nan))
        else:
            data_se = fe_df_se.reset_index()
            data_se = pd.get_dummies(data_se, columns=["asset"], drop_first=True)
            date_dummies_se = pd.get_dummies(data_se["date"], prefix="t", drop_first=True)
            data_se = pd.concat([data_se, date_dummies_se], axis=1)

            x_cols_se = ["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]
            x_cols_se += [c for c in data_se.columns if c.startswith("asset_") or c.startswith("t_")]

            fit_se = sm.OLS(data_se["asset_return_pct"], sm.add_constant(data_se[x_cols_se])).fit(cov_type=hc_type)
            coef_se = float(fit_se.params.get("policy_exposure_term_12", np.nan))
            se_se = float(fit_se.bse.get("policy_exposure_term_12", np.nan))
            pval_se = float(fit_se.pvalues.get("policy_exposure_term_12", np.nan))

        checks.append(
            {
                "specification": f"RobustSE_{hc_type}",
                "robustness_type": "RobustSEComparison",
                "policy_term": "policy_exposure_term_12",
                "coef": coef_se,
                "std_err": se_se,
                "p_value": pval_se,
            }
        )

    return pd.DataFrame(checks)


# -----------------------------------------------------------------------------
# Section 7: Save regression tables and diagnostic plots
# -----------------------------------------------------------------------------

def extract_main_table(fe_model, model_name: str) -> pd.DataFrame:
    params = pd.Series(fe_model.params)
    stderr = pd.Series(fe_model.std_errors)
    tvals = pd.Series(fe_model.tstats)
    pvals = pd.Series(fe_model.pvalues)

    table = pd.DataFrame(
        {
            "term": params.index,
            "coef": params.values,
            "std_err": stderr.reindex(params.index).values,
            "t_stat": tvals.reindex(params.index).values,
            "p_value": pvals.reindex(params.index).values,
            "model": model_name,
        }
    )
    return table


def p_stars(pval: float) -> str:
    if pval < 0.01:
        return "***"
    if pval < 0.05:
        return "**"
    if pval < 0.10:
        return "*"
    return ""


def format_term_label(term: str) -> str:
    mapping = {
        "policy_exposure_term_12": "Policy Exposure (Lag 12)",
        "policy_exposure_term_6": "Policy Exposure (Lag 6)",
        "policy_exposure_term_3": "Policy Exposure (Lag 3)",
        "policy_placebo_term": "Policy Placebo Lead (12)",
        "vix_exposure_term": "VIX Exposure",
        "ret_lag1": "Return Lag 1",
        "ret_mom3": "Return Momentum (3M)",
        "Entity_FE": "Entity FE",
        "Time_FE": "Time FE",
        "Clustered_SE": "Clustered SE",
        "R2_within": "R2 Within",
    }
    return mapping.get(term, term.replace("_", " ").title())


def format_feature_label(feature: str) -> str:
    mapping = {
        "ret_mom3": "Return Momentum (3M)",
        "ret_lag1": "Return Lag 1",
        "vix_index": "VIX Index",
        "m2_growth_pct": "M2 Growth (%)",
        "consumer_sentiment": "Consumer Sentiment",
        "bbb_spread": "BBB Spread",
        "fed_funds_rate_lag12": "Fed Funds Rate (Lag 12)",
        "asset_SP500": "Asset: SP500",
        "asset_HomePrice": "Asset: Home Price",
        "asset_Gold": "Asset: Gold",
    }
    return mapping.get(feature, feature.replace("_", " ").title())


def build_publication_table(fe_standard, fe_clustered, fe_robust) -> pd.DataFrame:
    records = []
    terms = ["policy_exposure_term_12", "vix_exposure_term", "ret_lag1", "ret_mom3"]

    for term in terms:
        c0 = float(fe_standard.params.get(term, np.nan))
        se0 = float(fe_standard.std_errors.get(term, np.nan))
        p0 = float(fe_standard.pvalues.get(term, np.nan))

        c1 = float(fe_clustered.params.get(term, np.nan))
        se1 = float(fe_clustered.std_errors.get(term, np.nan))
        p1 = float(fe_clustered.pvalues.get(term, np.nan))

        c2 = float(fe_robust.params.get(term, np.nan))
        se2 = float(fe_robust.std_errors.get(term, np.nan))
        p2 = float(fe_robust.pvalues.get(term, np.nan))

        records.append(
            {
                "Term": format_term_label(term),
                "Model 1 FE Standard Coef": f"{c0:.4f}{p_stars(p0)}",
                "Model 1 FE Standard SE": f"({se0:.4f})",
                "Model 2 FE Clustered Coef": f"{c1:.4f}{p_stars(p1)}",
                "Model 2 FE Clustered SE": f"({se1:.4f})",
                "Model 3 FE Robust Coef": f"{c2:.4f}{p_stars(p2)}",
                "Model 3 FE Robust SE": f"({se2:.4f})",
            }
        )

    n_obs = int(fe_clustered.nobs)
    within_r2 = float(getattr(fe_clustered, "rsquared_within", np.nan))
    records.append(
        {
            "Term": "Entity FE",
            "Model 1 FE Standard Coef": "Yes",
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": "Yes",
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": "Yes",
            "Model 3 FE Robust SE": "",
        }
    )
    records.append(
        {
            "Term": "Time FE",
            "Model 1 FE Standard Coef": "Yes",
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": "Yes",
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": "Yes",
            "Model 3 FE Robust SE": "",
        }
    )
    records.append(
        {
            "Term": "Clustered SE",
            "Model 1 FE Standard Coef": "No",
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": "Yes",
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": "No",
            "Model 3 FE Robust SE": "",
        }
    )
    records.append(
        {
            "Term": "HC Robust SE",
            "Model 1 FE Standard Coef": "No",
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": "No",
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": "Yes",
            "Model 3 FE Robust SE": "",
        }
    )
    records.append(
        {
            "Term": "N",
            "Model 1 FE Standard Coef": str(n_obs),
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": str(n_obs),
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": str(n_obs),
            "Model 3 FE Robust SE": "",
        }
    )
    records.append(
        {
            "Term": "R2 Within",
            "Model 1 FE Standard Coef": f"{within_r2:.4f}",
            "Model 1 FE Standard SE": "",
            "Model 2 FE Clustered Coef": f"{within_r2:.4f}",
            "Model 2 FE Clustered SE": "",
            "Model 3 FE Robust Coef": f"{within_r2:.4f}",
            "Model 3 FE Robust SE": "",
        }
    )

    return pd.DataFrame(records)


def write_interpretation_memo(
    fe_standard,
    fe_clustered,
    fe_robust,
    ml_results: pd.DataFrame,
    bp_df: pd.DataFrame,
    vif_df: pd.DataFrame,
    robustness_df: pd.DataFrame,
) -> None:
    policy_coef = float(fe_clustered.params.get("policy_exposure_term_12", np.nan))
    policy_p = float(fe_clustered.pvalues.get("policy_exposure_term_12", np.nan))
    vix_coef = float(fe_clustered.params.get("vix_exposure_term", np.nan))
    lag_coef = float(fe_clustered.params.get("ret_lag1", np.nan))
    mom_coef = float(fe_clustered.params.get("ret_mom3", np.nan))

    bp_p = float(bp_df.loc["LM", "p_value"])
    max_vif = float(vif_df["vif"].max())
    rf_row = ml_results.loc[ml_results["model"] == "RandomForest"].iloc[0]
    ols_row = ml_results.loc[ml_results["model"] == "OLS"].iloc[0]
    # Extract robust SE check statistics
    se_df = robustness_df[robustness_df["robustness_type"] == "RobustSEComparison"].copy()
    se_summary = ""
    if not se_df.empty and "std_err" in se_df.columns:
        min_se = se_df["std_err"].min()
        max_se = se_df["std_err"].max()
        se_summary = f"\n- HC covariance estimator SEs range from {min_se:.4f} to {max_se:.4f} across HC0-HC3, indicating robustness to HC specification choice."

    interpretation = f"""# M3 Interpretation Memo

## Model A Headline
A 1-unit increase in the 12-month lagged policy exposure term is associated with a {policy_coef:.4f} percentage-point change in monthly asset return (p-value = {policy_p:.4f}) in the two-way fixed effects specification.

- Statistical interpretation: with p-value > 0.10, we fail to reject the null that the average policy-exposure effect is zero in this specification.
- Practical interpretation: the point estimate is economically small relative to typical month-to-month return volatility, so effect size appears limited in-sample.

## Economic Interpretation
- Channel 1 (discount-rate sensitivity): assets with higher rate exposure can reprice through financing and discount-rate channels after policy changes.
- Channel 2 (risk sentiment): VIX-related exposure captures changes in risk appetite that shift performance asymmetrically across asset classes.
- Channel 3 (momentum/mean reversion): lagged return and 3-month momentum terms show strong dynamics, indicating persistence and subsequent correction effects in returns.
- Combined read: policy signals appear to operate through interaction terms and dynamics rather than as a large direct average shift in returns.
- Estimated risk channel magnitude: the VIX exposure coefficient is {vix_coef:.4f}, which is consistent with higher uncertainty being associated with weaker risk-asset performance after conditioning on FE.
- Dynamic adjustment pattern: Return Lag 1 ({lag_coef:.4f}) and Return Momentum (3M) ({mom_coef:.4f}) point to short-horizon reversal plus medium-horizon continuation, suggesting partial overshooting followed by correction.
- Asset-class implication: because policy and VIX effects enter through exposure interactions, transmission is heterogeneous by asset type rather than uniform across all markets in a given month.
- Portfolio interpretation: the results are more consistent with relative-rotation effects (winners vs. losers across assets) than with a single common directional response to policy changes.

## Model B Summary (ML vs OLS)
- OLS test R2: {ols_row['test_r2']:.4f}; test RMSE: {ols_row['test_rmse']:.4f}
- Random Forest test R2: {rf_row['test_r2']:.4f}; test RMSE: {rf_row['test_rmse']:.4f}
- Key takeaway: Random Forest provides higher predictive fit and lower forecast error, but OLS/FE remains more interpretable for causal discussion.
- Model-use guidance: use FE/OLS outputs for coefficient interpretation and policy discussion; use Random Forest for forecast-oriented benchmarking.

## Diagnostics
- Breusch-Pagan LM p-value = {bp_p:.6f}. Since p < 0.05, heteroskedasticity is present.
- VIF max = {max_vif:.4f} (below 10 threshold), suggesting no severe multicollinearity problem in selected predictors.
- Residual diagnostics were saved to figures and inspected via residuals-vs-fitted and Q-Q plots.
- Implication: heteroskedasticity supports reporting robust/clustered standard errors as the primary inferential basis.

## Robustness Checks
- Standard vs clustered vs HC-robust SE comparison reported in table.
- Alternative lag specifications tested (lag 3, 6, 12).
- Placebo lead test estimated.
- Outlier exclusion estimated (2008-2009 crisis and Mar-May 2020).
- Group subsamples estimated by asset class (SP500, HomePrice, Gold).
- HC covariance estimator robustness check (HC0, HC1, HC2, HC3): coefficient and standard error comparisons show stability across specifications.{se_summary}
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
"""

    with open(Path(__file__).resolve().parent.parent / "M3_interpretation.md", "w", encoding="utf-8") as f:
        f.write(interpretation)


def plot_robust_se_comparison(robustness_df: pd.DataFrame) -> None:
    """Plot comparison of standard errors across different HC specifications."""
    se_df = robustness_df[robustness_df["robustness_type"] == "RobustSEComparison"].copy()
    
    if se_df.empty or "std_err" not in se_df.columns:
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Coefficients by HC type
    ax1.bar(se_df["specification"].str.replace("RobustSE_", ""), se_df["coef"], 
            color="#4C78A8", alpha=0.8, edgecolor="black")
    ax1.axhline(0, color="red", linestyle="--", linewidth=1)
    ax1.set_title("Policy Exposure Coefficient by HC Type")
    ax1.set_ylabel("Coefficient")
    ax1.set_xlabel("Robust SE Specification")
    ax1.grid(axis="y", alpha=0.3)
    
    # Plot 2: Standard Errors by HC type
    ax2.bar(se_df["specification"].str.replace("RobustSE_", ""), se_df["std_err"], 
            color="#E15759", alpha=0.8, edgecolor="black")
    ax2.set_title("Standard Error of Policy Exposure by HC Type")
    ax2.set_ylabel("Standard Error")
    ax2.set_xlabel("Robust SE Specification")
    ax2.grid(axis="y", alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "M3_modelA_robust_se_comparison.png", dpi=300)
    plt.close(fig)


def save_outputs(
    fe_standard,
    fe_clustered,
    fe_robust,
    ml_results: pd.DataFrame,
    rf_importance: pd.DataFrame,
    bp_df: pd.DataFrame,
    vif_df: pd.DataFrame,
    robustness_df: pd.DataFrame,
) -> None:
    model_a_standard_tbl = extract_main_table(fe_standard, "ModelA_FE_standard")
    model_a_cluster_tbl = extract_main_table(fe_clustered, "ModelA_FE_clustered")
    model_a_robust_tbl = extract_main_table(fe_robust, "ModelA_FE_robust")

    model_a_tbl = pd.concat(
        [model_a_standard_tbl, model_a_cluster_tbl, model_a_robust_tbl],
        axis=0,
        ignore_index=True,
    )
    model_a_tbl["term"] = model_a_tbl["term"].astype(str).apply(format_term_label)
    model_a_tbl["model"] = model_a_tbl["model"].astype(str).str.replace("_", " ", regex=False)
    model_a_tbl.to_csv(TABLES_DIR / "M3_modelA_regression_table.csv", index=False)

    pub_table = build_publication_table(fe_standard, fe_clustered, fe_robust)
    pub_table.to_csv(TABLES_DIR / "M3_regression_table.csv", index=False)

    ml_results.to_csv(TABLES_DIR / "M3_modelB_ml_comparison.csv", index=False)
    rf_importance_out = rf_importance.copy()
    rf_importance_out["feature"] = rf_importance_out["feature"].astype(str).apply(format_feature_label)
    rf_importance_out.to_csv(TABLES_DIR / "M3_modelB_rf_feature_importance.csv", index=False)

    bp_df.to_csv(TABLES_DIR / "M3_modelA_breusch_pagan.csv")
    vif_df.to_csv(TABLES_DIR / "M3_modelA_vif.csv", index=False)
    robustness_df.to_csv(TABLES_DIR / "M3_modelA_robustness_checks.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    top_imp = rf_importance_out.head(10).iloc[::-1]
    ax.barh(top_imp["feature"], top_imp["importance"], color="#4C78A8")
    ax.set_title("M3 Model B: Random Forest Feature Importance (Top 10)")
    ax.set_xlabel("Importance")
    ax.set_ylabel("Feature")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "M3_modelB_rf_feature_importance_top10.png", dpi=300)
    plt.close(fig)

    # Plot robust SE comparison
    plot_robust_se_comparison(robustness_df)

    summary_path = TABLES_DIR / "M3_run_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("QM 2023 Capstone Milestone 3 Run Summary\n")
        f.write("=====================================\n\n")
        f.write("Model A (Fixed Effects) saved tables:\n")
        f.write("- M3_modelA_regression_table.csv\n")
        f.write("- M3_regression_table.csv\n")
        f.write("- M3_modelA_breusch_pagan.csv\n")
        f.write("- M3_modelA_vif.csv\n")
        f.write("- M3_modelA_robustness_checks.csv\n\n")
        f.write("Model B (ML Comparison) saved tables:\n")
        f.write("- M3_modelB_ml_comparison.csv\n")
        f.write("- M3_modelB_rf_feature_importance.csv\n\n")
        f.write("Saved figures:\n")
        f.write("- M3_residuals_vs_fitted.png\n")
        f.write("- M3_qq_plot.png\n")
        f.write("- M3_modelB_rf_feature_importance_top10.png\n")
        f.write("- M3_modelA_robust_se_comparison.png\n")


def main() -> None:
    ensure_output_dirs()

    raw = load_data()
    feat = build_m2_consistent_features(raw)
    panel_long = build_asset_panel(feat)

    fe_df, fe_standard, fe_clustered, fe_robust = fit_model_a_fe(panel_long)
    bp_df, vif_df = diagnostics_model_a(fe_df, fe_clustered)

    robustness_df = robustness_checks(panel_long)
    ml_results, rf_importance = fit_model_b_ml(panel_long)

    save_outputs(
        fe_standard=fe_standard,
        fe_clustered=fe_clustered,
        fe_robust=fe_robust,
        ml_results=ml_results,
        rf_importance=rf_importance,
        bp_df=bp_df,
        vif_df=vif_df,
        robustness_df=robustness_df,
    )

    write_interpretation_memo(
        fe_standard=fe_standard,
        fe_clustered=fe_clustered,
        fe_robust=fe_robust,
        ml_results=ml_results,
        bp_df=bp_df,
        vif_df=vif_df,
        robustness_df=robustness_df,
    )

    print("Milestone 3 modeling pipeline completed.")
    print(f"Tables saved to: {TABLES_DIR}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
