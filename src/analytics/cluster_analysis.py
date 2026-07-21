import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# =====================================================
# Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"
REPORT_DIR = PROJECT_ROOT / "reports"

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


# =====================================================
# Load Data
# =====================================================

def load_cluster_data():
    labels = pd.read_csv(OUTPUT_DIR / "cluster_labels.csv")
    summary = pd.read_csv(OUTPUT_DIR / "cluster_summary.csv")

    conn = sqlite3.connect(DB_PATH)

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn,
    )

    conn.close()

    return labels, summary, sectors


# =====================================================
# Prepare Dataset
# =====================================================

def prepare_dataset():
    labels, summary, sectors = load_cluster_data()

    df = labels.merge(
        sectors,
        on="company_id",
        how="left",
    )

    return df, summary


# =====================================================
# Company Count
# =====================================================

def company_count(df):
    return (
        df.groupby("cluster_id")
        .size()
        .reset_index(name="companies")
    )


# =====================================================
# Sector Distribution
# =====================================================

def sector_distribution(df):
    return (
        df.groupby(
            ["cluster_id", "broad_sector"]
        )
        .size()
        .reset_index(name="count")
    )


# =====================================================
# Cluster Insights
# =====================================================

def create_cluster_insights(summary, company_counts):

    cluster_names = {
        0: "Stable Performers",
        1: "High Profit Leaders",
        2: "Financial Outliers",
        3: "Leveraged Growth",
        4: "Cash Rich Leaders",
    }

    investment_profiles = {
        0: "Balanced companies with steady profitability and low leverage.",
        1: "Companies with outstanding profitability and strong operational efficiency.",
        2: "Companies showing extreme financial metrics that require detailed analysis.",
        3: "High-growth companies financed with significant debt.",
        4: "Cash-rich mature companies generating strong operating cash flows.",
    }

    insights = summary.merge(
        company_counts,
        on="cluster_id",
        how="left",
    )

    insights["cluster_name"] = insights["cluster_id"].map(cluster_names)

    insights["investment_profile"] = insights["cluster_id"].map(
        investment_profiles
    )

    insights = insights[
        [
            "cluster_id",
            "cluster_name",
            "companies",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "net_cash_flow",
            "operating_profit_margin_pct",
            "investment_profile",
        ]
    ]

    insights.to_csv(
        OUTPUT_DIR / "cluster_insights.csv",
        index=False,
    )

    print("\n✅ cluster_insights.csv saved")

    return insights


# =====================================================
# Visualization 1
# =====================================================

def plot_cluster_distribution(company_counts):

    plt.figure(figsize=(8, 5))

    plt.bar(
        company_counts["cluster_id"].astype(str),
        company_counts["companies"],
    )

    plt.title("Companies per Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Number of Companies")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "cluster_distribution.png",
        dpi=300,
    )

    plt.close()

    print("✅ cluster_distribution.png saved")


# =====================================================
# Visualization 2
# =====================================================

def plot_feature_comparison(summary):

    features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "operating_profit_margin_pct",
    ]

    plot_df = summary.set_index("cluster_id")[features]

    plot_df.plot(
        kind="bar",
        figsize=(12, 6),
    )

    plt.title("Financial Metrics by Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Average Value")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "cluster_feature_comparison.png",
        dpi=300,
    )

    plt.close()

    print("✅ cluster_feature_comparison.png saved")


# =====================================================
# Visualization 3
# =====================================================

def plot_sector_distribution(sectors):

    pivot = sectors.pivot(
        index="cluster_id",
        columns="broad_sector",
        values="count",
    ).fillna(0)

    pivot.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 6),
    )

    plt.title("Sector Distribution by Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Companies")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "sector_distribution.png",
        dpi=300,
    )

    plt.close()

    print("✅ sector_distribution.png saved")


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    df, summary = prepare_dataset()

    company_counts = company_count(df)

    sectors = sector_distribution(df)

    print("\n========== CLUSTER SUMMARY ==========")
    print(summary)

    print("\n========== COMPANY COUNT ==========")
    print(company_counts)

    print("\n========== SECTOR DISTRIBUTION ==========")
    print(sectors)

    insights = create_cluster_insights(
        summary,
        company_counts,
    )

    print("\n========== CLUSTER INSIGHTS ==========")
    print(insights)

    plot_cluster_distribution(company_counts)

    plot_feature_comparison(summary)

    plot_sector_distribution(sectors)

    print("\n🎉 Cluster analysis completed successfully.")