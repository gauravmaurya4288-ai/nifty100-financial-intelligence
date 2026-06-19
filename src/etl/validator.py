import pandas as pd
from datetime import datetime

# Store validation failures
failures = []


def log_failure(rule_id, severity, table_name, record_id, message):
    failures.append({
        "rule_id": rule_id,
        "severity": severity,
        "table_name": table_name,
        "record_id": record_id,
        "message": message,
        "timestamp": datetime.now()
    })


# DQ-01 Primary Key Uniqueness
def dq01_pk_uniqueness(df, pk_column, table_name):

    duplicates = df[
        df.duplicated(
            subset=[pk_column],
            keep=False
        )
    ]

    for _, row in duplicates.iterrows():

        log_failure(
            "DQ-01",
            "CRITICAL",
            table_name,
            row[pk_column],
            "Duplicate Primary Key"
        )


# DQ-02 Composite Key Validation
def dq02_composite_pk(df, columns, table_name):

    duplicates = df[
        df.duplicated(
            subset=columns,
            keep=False
        )
    ]

    for _, row in duplicates.iterrows():

        log_failure(
            "DQ-02",
            "CRITICAL",
            table_name,
            str(tuple(row[col] for col in columns)),
            "Duplicate Composite Key"
        )


# DQ-03 Foreign Key Integrity
def dq03_fk_integrity(child_df, parent_df, fk_column, table_name):

    invalid = child_df[
        ~child_df[fk_column].isin(
            parent_df[fk_column]
        )
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-03",
            "CRITICAL",
            table_name,
            row[fk_column],
            "Foreign Key Violation"
        )

def dq04_null_check(
    df,
    column,
    table_name
):

    invalid = df[
        df[column].isnull()
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-04",
            "CRITICAL",
            table_name,
            "NULL",
            f"{column} is NULL"
        ) 

        
# Save validation results
def save_failures():

    if not failures:

        print("No validation failures found.")
        return

    pd.DataFrame(failures).to_csv(
        "output/validation_failures.csv",
        index=False
    )

    print(
        f"{len(failures)} validation failures saved."
    )

def dq06_invalid_ticker(df, ticker_column, table_name):

    invalid = df[
        df[ticker_column].str.strip() == ""
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-06",
            "CRITICAL",
            table_name,
            row.name,
            "Invalid Ticker"
        )
def dq07_missing_company_master(
    child_df,
    master_df,
    company_column,
    table_name
):

    invalid = child_df[
        ~child_df[company_column].isin(
            master_df[company_column]
        )
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-07",
            "CRITICAL",
            table_name,
            row[company_column],
            "Company Missing In Master"
        )

def dq07_missing_company_master(
    child_df,
    master_df,
    company_column,
    table_name
):

    invalid = child_df[
        ~child_df[company_column].isin(
            master_df[company_column]
        )
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-07",
            "CRITICAL",
            table_name,
            row[company_column],
            "Company Missing In Master"
        )

def dq08_duplicate_stock_prices(df):

    duplicates = df[
        df.duplicated(
            subset=["company_id", "date"],
            keep=False
        )
    ]

    for _, row in duplicates.iterrows():

        log_failure(
            "DQ-08",
            "CRITICAL",
            "stock_prices",
            row["company_id"],
            "Duplicate Stock Price Record"
        )
def dq09_negative_revenue(df):

    invalid = df[
        df["revenue"] < 0
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-09",
            "WARNING",
            "profit_loss",
            row["company_id"],
            "Negative Revenue"
        )
def dq10_operating_margin(df):

    invalid = df[
        df["operating_margin"] > 100
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-10",
            "WARNING",
            "ratios",
            row["company_id"],
            "Operating Margin Greater Than 100%"
        )
def dq11_balance_sheet_mismatch(df):

    invalid = df[
        abs(
            df["total_assets"]
            -
            (
                df["total_liabilities"]
                +
                df["equity"]
            )
        ) > 1
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-11",
            "WARNING",
            "balance_sheet",
            row["company_id"],
            "Balance Sheet Mismatch"
        )

def dq12_cashflow_mismatch(df):

    invalid = df[
        abs(
            df["operating_cf"]
            +
            df["investing_cf"]
            +
            df["financing_cf"]
            -
            df["net_cash_flow"]
        ) > 1
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-12",
            "WARNING",
            "cash_flow",
            row["company_id"],
            "Cash Flow Mismatch"
        )

def dq13_missing_sector(df):

    invalid = df[
        df["sector"].isnull()
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-13",
            "WARNING",
            "companies",
            row["company_id"],
            "Sector Missing"
        )

def dq14_missing_industry(df):

    invalid = df[
        df["industry"].isnull()
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-14",
            "WARNING",
            "companies",
            row["company_id"],
            "Industry Missing"
        )
def dq14_missing_industry(df):

    invalid = df[
        df["industry"].isnull()
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-14",
            "WARNING",
            "companies",
            row["company_id"],
            "Industry Missing"
        )

def dq15_missing_market_cap(df):

    invalid = df[
        df["market_cap"].isnull()
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-15",
            "WARNING",
            "market_cap",
            row["company_id"],
            "Market Cap Missing"
        )

def dq16_less_than_5_years_history(df):

    years = (
        df.groupby("company_id")["year"]
        .nunique()
        .reset_index()
    )

    invalid = years[
        years["year"] < 5
    ]

    for _, row in invalid.iterrows():

        log_failure(
            "DQ-16",
            "WARNING",
            "financials",
            row["company_id"],
            "Less Than 5 Years History"
        )                            
if __name__ == "__main__":

    print("===================================")
    print("Running Data Quality Checks...")
    print("===================================")

    # DQ checks will be called here later

    save_failures()
if __name__ == "__main__":

    print("Running Data Quality Checks...")

    companies = pd.DataFrame({
        "company_id": [1, 1, None]
    })

    dq01_pk_uniqueness(
        companies,
        "company_id",
        "companies"
    )

    dq04_null_check(
        companies,
        "company_id",
        "companies"
    )

    save_failures()

    print("Validation Completed")
    print("===================================")
    print("Validation Completed")
    print("===================================")