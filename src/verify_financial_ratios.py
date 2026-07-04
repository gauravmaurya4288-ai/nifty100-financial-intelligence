import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("=" * 70)
print("FINANCIAL RATIOS VERIFICATION")
print("=" * 70)

# -------------------------------------------------------
# Row Count
# -------------------------------------------------------

count = pd.read_sql(
    """
    SELECT COUNT(*) AS total_rows
    FROM financial_ratios
    """,
    conn
)

print("\nTotal Rows")
print(count)

# -------------------------------------------------------
# Sample Records
# -------------------------------------------------------

sample = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    LIMIT 5
    """,
    conn
)

print("\nSample Records")
print(sample)

# -------------------------------------------------------
# Composite Score Statistics
# -------------------------------------------------------

score = pd.read_sql(
    """
    SELECT
        ROUND(AVG(composite_quality_score),2) AS avg_score,
        ROUND(MAX(composite_quality_score),2) AS max_score,
        ROUND(MIN(composite_quality_score),2) AS min_score
    FROM financial_ratios
    """,
    conn
)

print("\nComposite Score")
print(score)

# -------------------------------------------------------
# CAGR Availability
# -------------------------------------------------------

cagr = pd.read_sql(
    """
    SELECT
        COUNT(revenue_cagr_5yr) AS revenue_cagr,
        COUNT(pat_cagr_5yr) AS pat_cagr,
        COUNT(eps_cagr_5yr) AS eps_cagr
    FROM financial_ratios
    """,
    conn
)

print("\nCAGR Columns")
print(cagr)

# -------------------------------------------------------
# Null Count Per Column
# -------------------------------------------------------

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("\nNull Values")

nulls = (
    df.isnull()
      .sum()
      .sort_values(ascending=False)
)

print(nulls)

# -------------------------------------------------------
# Top 10 Companies
# -------------------------------------------------------

top10 = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        composite_quality_score
    FROM financial_ratios
    ORDER BY composite_quality_score DESC
    LIMIT 10
    """,
    conn
)

print("\nTop 10 Companies")
print(top10)

# -------------------------------------------------------
# Save Verification Report
# -------------------------------------------------------

with pd.ExcelWriter("output/financial_ratios_verification.xlsx") as writer:

    count.to_excel(writer,
                   sheet_name="Row Count",
                   index=False)

    sample.to_excel(writer,
                    sheet_name="Sample",
                    index=False)

    score.to_excel(writer,
                   sheet_name="Composite Score",
                   index=False)

    cagr.to_excel(writer,
                  sheet_name="CAGR",
                  index=False)

    nulls.to_frame("Null Count").to_excel(
        writer,
        sheet_name="Null Values"
    )

    top10.to_excel(writer,
                   sheet_name="Top 10",
                   index=False)

print("\nVerification report saved to:")
print("output/financial_ratios_verification.xlsx")

conn.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETED SUCCESSFULLY")
print("=" * 70)