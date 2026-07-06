import pandas as pd


# =====================================================
# Quality Compounder
# =====================================================

def quality_compounder(df: pd.DataFrame):

    result = df[

        (df["return_on_equity_pct"] > 15)

        &

        (df["debt_to_equity"] < 1)

        &

        (df["free_cash_flow_cr"] > 0)

        &

        (df["revenue_cagr_5yr"] > 10)

    ]

    return result.sort_values(

        "composite_quality_score",

        ascending=False

    )


# =====================================================
# Value Pick
# =====================================================

def value_pick(df: pd.DataFrame):

    result = df[

        (df["pe_ratio"] < 20)

        &

        (df["pb_ratio"] < 3)

        &

        (df["dividend_yield_pct"] > 1)

    ]

    return result.sort_values(

        "pe_ratio"

    )


# =====================================================
# Growth Accelerator
# =====================================================

def growth_accelerator(df: pd.DataFrame):

    result = df[

        (df["pat_cagr_5yr"] > 20)

        &

        (df["revenue_cagr_5yr"] > 15)

        &

        (df["debt_to_equity"] < 2)

    ]

    return result.sort_values(

        "pat_cagr_5yr",

        ascending=False

    )


# =====================================================
# Dividend Champion
# =====================================================

def dividend_champion(df: pd.DataFrame):

    result = df[

        (df["dividend_yield_pct"] > 2)

        &

        (df["dividend_payout_ratio_pct"] < 80)

        &

        (df["free_cash_flow_cr"] > 0)

    ]

    return result.sort_values(

        "dividend_yield_pct",

        ascending=False

    )


# =====================================================
# Debt Free Blue Chip
# =====================================================

def debt_free_bluechip(df: pd.DataFrame):

    result = df[

        (df["total_debt_cr"] <= 0)

        &

        (df["return_on_equity_pct"] > 12)

        &

        (df["interest_coverage"] > 5)

        &

        (df["free_cash_flow_cr"] > 0)

    ]

    return result.sort_values(

        "composite_quality_score",

        ascending=False

    )


# =====================================================
# Turnaround Watch
# =====================================================

def turnaround_watch(df: pd.DataFrame):

    result = df[

        (df["free_cash_flow_cr"] > 0)

        &

        (df["revenue_cagr_5yr"] > 5)

        &

        (df["debt_to_equity"] < 3)

        &

        (df["return_on_equity_pct"] > 10)

    ]

    return result.sort_values(

        "revenue_cagr_5yr",

        ascending=False

    )


# =====================================================
# Summary
# =====================================================

def summary(results):

    print("\n" + "=" * 60)

    print("PRESET SUMMARY")

    print("=" * 60)

    for name, frame in results.items():

        print(f"{name:<25} {len(frame)}")

    print("=" * 60)