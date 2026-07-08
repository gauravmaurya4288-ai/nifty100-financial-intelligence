import pandas as pd
import numpy as np


# ==========================================================
# Normalize (0–100)
# ==========================================================

def normalize(series: pd.Series):

    s = series.copy()

    s = s.fillna(s.median())

    minimum = s.min()

    maximum = s.max()

    if maximum == minimum:
        return pd.Series(50, index=s.index)

    return ((s - minimum) / (maximum - minimum)) * 100


# ==========================================================
# Reverse Normalize
# Lower is Better
# ==========================================================

def reverse_normalize(series):

    s = normalize(series)

    return 100 - s


# ==========================================================
# Winsorization
# Remove Outliers
# ==========================================================

def winsorize(series):

    lower = series.quantile(0.10)

    upper = series.quantile(0.90)

    return series.clip(lower, upper)


# ==========================================================
# Composite Score
# ==========================================================

def calculate_scores(df):

    data = df.copy()

    # ----------------------------------------

    data["roe_score"] = normalize(

        winsorize(

            data["return_on_equity_pct"]

        )

    )

    data["roce_score"] = normalize(

        winsorize(

            data["return_on_capital_employed_pct"]

        )

    )

    data["npm_score"] = normalize(

        winsorize(

            data["net_profit_margin_pct"]

        )

    )

    data["fcf_score"] = normalize(

        winsorize(

            data["free_cash_flow_cr"]

        )

    )

    data["revenue_score"] = normalize(

        winsorize(

            data["revenue_cagr_5yr"]

        )

    )

    data["pat_score"] = normalize(

        winsorize(

            data["pat_cagr_5yr"]

        )

    )

    data["asset_score"] = normalize(

        winsorize(

            data["asset_turnover"]

        )

    )

    data["icr_score"] = normalize(

        winsorize(

            data["interest_coverage"]

        )

    )

    data["de_score"] = reverse_normalize(

        winsorize(

            data["debt_to_equity"]

        )

    )

    # ----------------------------------------
    # Composite
    # ----------------------------------------

    data["composite_quality_score"] = (

        data["roe_score"] * 0.15 +

        data["roce_score"] * 0.10 +

        data["npm_score"] * 0.10 +

        data["fcf_score"] * 0.15 +

        data["revenue_score"] * 0.10 +

        data["pat_score"] * 0.10 +

        data["asset_score"] * 0.05 +

        data["icr_score"] * 0.05 +

        data["de_score"] * 0.20

    )

    data["composite_quality_score"] = (

        data["composite_quality_score"]

        .round(2)

    )

    return data