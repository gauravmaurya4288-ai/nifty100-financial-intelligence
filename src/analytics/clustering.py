import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from scipy.spatial.distance import cdist

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_company_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.company_id,
        c.company_name,

        s.broad_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.operating_profit_margin_pct,

        cf.net_cash_flow

    FROM companies c

    INNER JOIN sectors s
        ON c.company_id = s.company_id

    INNER JOIN financial_ratios fr
        ON c.company_id = fr.company_id

    INNER JOIN cash_flow cf
        ON c.company_id = cf.company_id
        AND fr.year = cf.year

    WHERE fr.year = (
        SELECT MAX(fr2.year)
        FROM financial_ratios fr2
        WHERE fr2.company_id = c.company_id
    )
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "net_cash_flow",
    "operating_profit_margin_pct",
]

def impute_missing_values(df):

    df = df.copy()

    for col in FEATURES:

        df[col] = (
            df.groupby("broad_sector")[col]
              .transform(lambda x: x.fillna(x.median()))
        )

        df[col] = df[col].fillna(df[col].median())

    return df

def scale_features(df):

    scaler = StandardScaler()

    X = scaler.fit_transform(df[FEATURES])

    return X, scaler

def train_kmeans(X):

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)

    return model, labels

from scipy.spatial.distance import cdist

def compute_distance(model, X):

    distances = cdist(X, model.cluster_centers_)

    return distances.min(axis=1)

def save_clusters(df, labels, distances):

    names = {
        0: "Cluster 0",
        1: "Cluster 1",
        2: "Cluster 2",
        3: "Cluster 3",
        4: "Cluster 4",
    }

    output = pd.DataFrame({
        "company_id": df["company_id"],
        "company_name": df["company_name"],
        "cluster_id": labels,
        "cluster_name": [names[i] for i in labels],
        "distance_from_centroid": distances,
    })

    output.to_csv(
        OUTPUT_DIR / "cluster_labels.csv",
        index=False,
    )

    print("✅ cluster_labels.csv saved")

def plot_elbow_curve(X):
    inertias = []

    for k in range(2, 11):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )
        model.fit(X)
        inertias.append(model.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(range(2, 11), inertias, marker="o")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method for Optimal K")
    plt.grid(True)

    plt.savefig(REPORT_DIR / "elbow_plot.png", dpi=300)
    plt.close()

    print("✅ elbow_plot.png saved")

def create_cluster_summary(df):

    summary = (
        df.groupby("cluster_id")[FEATURES]
          .mean()
          .round(2)
    )

    summary.to_csv(
        OUTPUT_DIR / "cluster_summary.csv"
    )

    print("✅ cluster_summary.csv saved")







if __name__ == "__main__":

    df = load_company_data()

    print("Loaded:", len(df), "companies")

    df = impute_missing_values(df)

    X, scaler = scale_features(df)

    model, labels = train_kmeans(X)

    distances = compute_distance(model, X)

    # Add results back to the DataFrame
    df["cluster_id"] = labels
    df["distance_from_centroid"] = distances

    save_clusters(df, labels, distances)

    plot_elbow_curve(X)

    create_cluster_summary(df)