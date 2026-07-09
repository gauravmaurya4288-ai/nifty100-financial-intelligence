import sys
from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Database
# ==========================================================

DB = PROJECT_ROOT / "db" / "nifty100.db"

conn = sqlite3.connect(DB)

print("=" * 80)
print("DAY 19 - RADAR CHART ENGINE")
print("=" * 80)

# ==========================================================
# Load Tables
# ==========================================================

print("\nLoading Tables...\n")

financial = pd.read_sql(

    "SELECT * FROM financial_ratios",

    conn

)

peer_groups = pd.read_sql(

    "SELECT * FROM peer_groups",

    conn

)

print("Financial Ratios :", financial.shape)

print("Peer Groups      :", peer_groups.shape)

# ==========================================================
# Merge
# ==========================================================

df = financial.merge(

    peer_groups,

    on="company_id",

    how="left"

)

print()

print("Merged Shape :", df.shape)

# ==========================================================
# Radar Metrics
# ==========================================================

metrics = [

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "composite_quality_score"

]

# ==========================================================
# Peer Group Average
# ==========================================================

peer_average = (

    df

    .groupby(

        "peer_group_name"

    )[metrics]

    .mean(

        numeric_only=True

    )

    .reset_index()

)

print()

print("Peer Average Shape :", peer_average.shape)

print()

print(peer_average.head())

# ==========================================================
# Nifty100 Average
# ==========================================================

overall_average = (

    df[metrics]

    .mean(

        numeric_only=True

    )

)

print()

print("=" * 80)

print("Overall Nifty100 Average")

print("=" * 80)

print(overall_average)

# ==========================================================
# Merge Peer Average
# ==========================================================

df = df.merge(

    peer_average,

    on="peer_group_name",

    suffixes=(

        "",

        "_peer"

    ),

    how="left"

)

print()

print("Working Shape :", df.shape)

print()

print(df.head())

# ==========================================================
# Output Folder
# ==========================================================

REPORT_DIR = PROJECT_ROOT / "reports" / "radar_charts"

REPORT_DIR.mkdir(

    parents=True,

    exist_ok=True

)

print()

print("Radar Folder")

print(REPORT_DIR)

print()

# ==========================================================
# Radar Chart Function
# ==========================================================

import matplotlib.pyplot as plt

# Labels shown on the radar chart
labels = [

    "ROE",
    "ROCE",
    "NPM",
    "D/E",
    "FCF",
    "Revenue CAGR",
    "PAT CAGR",
    "Composite"

]

def normalize_values(values, minimums, maximums):
    """
    Normalize values to 0-100 so all metrics are comparable.
    """
    output = []

    for value, mn, mx in zip(values, minimums, maximums):

        if pd.isna(value):
            value = mn

        if mx == mn:
            output.append(50)
        else:
            output.append(((value - mn) / (mx - mn)) * 100)

    return output


def create_radar(company_row):

    company = company_row["company_id"]

    peer = company_row["peer_group_name"]

    # ---------------------------------------------
    # Company values
    # ---------------------------------------------

    company_values = [

        company_row["return_on_equity_pct"],
        company_row["return_on_capital_employed_pct"],
        company_row["net_profit_margin_pct"],
        company_row["debt_to_equity"],
        company_row["free_cash_flow_cr"],
        company_row["revenue_cagr_5yr"],
        company_row["pat_cagr_5yr"],
        company_row["composite_quality_score"]

    ]

    # ---------------------------------------------
    # Peer / Overall Average
    # ---------------------------------------------

    if pd.isna(peer):

        average_values = overall_average.tolist()

    else:

        average_values = [

            company_row["return_on_equity_pct_peer"],
            company_row["return_on_capital_employed_pct_peer"],
            company_row["net_profit_margin_pct_peer"],
            company_row["debt_to_equity_peer"],
            company_row["free_cash_flow_cr_peer"],
            company_row["revenue_cagr_5yr_peer"],
            company_row["pat_cagr_5yr_peer"],
            company_row["composite_quality_score_peer"]

        ]

    # ---------------------------------------------
    # Normalize
    # ---------------------------------------------

    mins = []

    maxs = []

    for m in metrics:

        mins.append(df[m].quantile(0.05))

        maxs.append(df[m].quantile(0.95))

    company_plot = normalize_values(company_values, mins, maxs)
    average_plot = normalize_values(average_values, mins, maxs)

    # Reverse Debt/Equity (lower is better)
    company_plot[3] = 100 - company_plot[3]
    average_plot[3] = 100 - average_plot[3]

    # Close polygons
    company_plot += company_plot[:1]
    average_plot += average_plot[:1]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    # ---------------------------------------------
    # Plot
    # ---------------------------------------------

    fig = plt.figure(figsize=(8, 8))

    ax = plt.subplot(111, polar=True)

    ax.plot(
        angles,
        company_plot,
        linewidth=2,
        label=company
    )

    ax.fill(
        angles,
        company_plot,
        alpha=0.25
    )

    ax.plot(
        angles,
        average_plot,
        linestyle="--",
        linewidth=2,
        label="Peer Average" if pd.notna(peer) else "Nifty100 Average"
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_ylim(0, 100)

    title = (
    f"{company}\n"
    f"Financial Performance Radar"
)

    ax.set_title(
        title,
        fontsize=18,
        fontweight="bold",
        color="darkblue",
        pad=20
    )

    ax.legend(loc="upper right")

    output = REPORT_DIR / f"{company}_radar.png"

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    # ==========================================================
# Generate Radar Charts
# ==========================================================

print("\n" + "=" * 80)
print("GENERATING RADAR CHARTS")
print("=" * 80)

# ----------------------------------------------------------
# Latest record for each company
# ----------------------------------------------------------

latest_df = (

    df

    .sort_values("year")

    .groupby("company_id", as_index=False)

    .tail(1)

)

print(f"Companies to Process : {len(latest_df)}")

generated = 0
failed = 0

for _, row in latest_df.iterrows():

    try:

        create_radar(row)

        generated += 1

        print(f"✓ {row['company_id']}")

    except Exception as e:

        failed += 1

        print(f"✗ {row['company_id']} -> {e}")

print()

print("=" * 80)
print("RADAR CHART SUMMARY")
print("=" * 80)

print(f"Charts Generated : {generated}")
print(f"Charts Failed    : {failed}")

print()
print("Output Folder")
print(REPORT_DIR)

# ==========================================================
# Final Summary
# ==========================================================

conn.close()

print()

print("=" * 80)
print("DAY 19 COMPLETED")
print("=" * 80)

print()

print("Generated Radar Charts Successfully")

print()

print("Reports Location")

print(REPORT_DIR)

print()
