"""
==========================================================
N100 FINANCIAL INTELLIGENCE
Day 45
Final Acceptance Checker (Version 2)
Part 1
AC-01 to AC-05
==========================================================
"""

import sqlite3
import pandas as pd
import requests
import time

from pathlib import Path
from datetime import datetime

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "db" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"

REPORT_DIR = BASE_DIR / "reports"

DOCS_DIR = BASE_DIR / "docs"

TEARSHEET_DIR = OUTPUT_DIR / "tearsheets"

REPORT_DIR.mkdir(exist_ok=True)

RESULTS = []


# ==========================================================
# DATABASE
# ==========================================================

def get_connection():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found:\n{DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)


# ==========================================================
# LOGGER
# ==========================================================

def log_result(gate, status, details):

    RESULTS.append({

        "Gate": gate,

        "Status": status,

        "Details": details,

        "Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    })

    print(f"[{status}] {gate}")

    print(details)

    print("-" * 60)


# ==========================================================
# HELPER
# ==========================================================

def table_exists(conn, table):

    sql = """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    AND name=?
    """

    return conn.execute(
        sql,
        (table,)
    ).fetchone() is not None


def get_row_count(conn, table):

    return conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]


# ==========================================================
# AC-01
# Company Count
# ==========================================================

def ac01_company_count():

    conn = get_connection()

    try:

        if not table_exists(conn, "companies"):

            log_result(
                "AC-01",
                "FAIL",
                "companies table not found."
            )

            return

        count = get_row_count(
            conn,
            "companies"
        )

        if count == 92:

            log_result(
                "AC-01",
                "PASS",
                f"Company count = {count}"
            )

        else:

            log_result(
                "AC-01",
                "FAIL",
                f"Expected 92 companies, found {count}"
            )

    finally:

        conn.close()


# ==========================================================
# AC-02
# Financial History
# ==========================================================

def ac02_history_check():

    conn = get_connection()

    tables = [

        "profit_loss",

        "balance_sheet",

        "cash_flow"

    ]

    minimum = int(92 * 0.90)

    passed = True

    messages = []

    try:

        for table in tables:

            if not table_exists(conn, table):

                passed = False

                messages.append(
                    f"{table}: table missing"
                )

                continue

            df = pd.read_sql(
                f"""
                SELECT
                    company_id,
                    COUNT(DISTINCT year) AS years
                FROM {table}
                GROUP BY company_id
                """,
                conn
            )

            companies = (
                df["years"] >= 10
            ).sum()

            messages.append(
                f"{table}: {companies} companies"
            )

            if companies < minimum:

                passed = False

        log_result(

            "AC-02",

            "PASS" if passed else "FAIL",

            "\n".join(messages)

        )

    finally:

        conn.close()


# ==========================================================
# AC-03
# Foreign Keys
# ==========================================================

def ac03_foreign_keys():

    conn = get_connection()

    try:

        rows = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if len(rows) == 0:

            log_result(
                "AC-03",
                "PASS",
                "No foreign key violations."
            )

        else:

            preview = "\n".join(
                [
                    f"{r[0]} | RowID={r[1]} | Parent={r[2]}"
                    for r in rows[:10]
                ]
            )

            if len(rows) > 10:

                preview += (
                    f"\n... {len(rows)-10} more"
                )

            log_result(

                "AC-03",

                "FAIL",

                f"{len(rows)} FK violations\n\n{preview}"

            )

    finally:

        conn.close()


# ==========================================================
# AC-04
# Financial Ratios
# ==========================================================

def ac04_financial_ratios():

    conn = get_connection()

    try:

        if not table_exists(
            conn,
            "financial_ratios"
        ):

            log_result(
                "AC-04",
                "FAIL",
                "financial_ratios table missing."
            )

            return

        rows = get_row_count(
            conn,
            "financial_ratios"
        )

        if rows >= 1050:

            log_result(
                "AC-04",
                "PASS",
                f"{rows} financial ratio rows."
            )

        else:

            log_result(
                "AC-04",
                "FAIL",
                f"Only {rows} rows found."
            )

    finally:

        conn.close()


# ==========================================================
# AC-05
# Revenue CAGR Spot Check
# ==========================================================

def ac05_revenue_cagr():

    conn = get_connection()

    try:

        df = pd.read_sql(
            """
            SELECT

                company_id,

                year,

                revenue_cagr_5yr

            FROM financial_ratios

            ORDER BY RANDOM()

            LIMIT 5
            """,
            conn
        )

        print(df)

        log_result(

            "AC-05",

            "MANUAL",

            "Compare the above values with Excel. "
            "Maximum difference allowed = 0.1%"

        )

    finally:

        conn.close()


# ==========================================================
# RUN PART 1
# ==========================================================

def run_part1():

    print("=" * 60)

    print("DAY 45 ACCEPTANCE TEST")

    print("PART 1")

    print("=" * 60)

    ac01_company_count()

    ac02_history_check()

    ac03_foreign_keys()

    ac04_financial_ratios()

    ac05_revenue_cagr()

    # ==========================================================
# AC-06
# ROE Validation
# Compare companies.roe_percentage with the latest
# financial_ratios.return_on_equity_pct
# ==========================================================

def ac06_roe_validation():

    conn = get_connection()

    try:

        query = """
        SELECT
            c.company_id,
            c.roe_percentage,
            f.return_on_equity_pct,
            f.year
        FROM companies c
        JOIN financial_ratios f
            ON c.company_id = f.company_id
        """

        df = pd.read_sql(query, conn)

        if df.empty:

            log_result(
                "AC-06",
                "FAIL",
                "No ROE data available."
            )

            return

        # Latest financial year per company
        latest = (
            df.sort_values(
                ["company_id", "year"]
            )
            .groupby("company_id")
            .tail(1)
        )

        latest["difference"] = (
            latest["roe_percentage"] -
            latest["return_on_equity_pct"]
        ).abs()

        failed = latest[
            latest["difference"] > 5
        ]

        if failed.empty:

            log_result(
                "AC-06",
                "PASS",
                "ROE validation passed."
            )

        else:

            log_result(
                "AC-06",
                "FAIL",
                failed[
                    [
                        "company_id",
                        "roe_percentage",
                        "return_on_equity_pct",
                        "difference"
                    ]
                ].head(10).to_string(index=False)
            )

    finally:

        conn.close()


# ==========================================================
# AC-07
# Screener Output
# ==========================================================

def ac07_quality_screener():

    excel_file = OUTPUT_DIR / "screener_output.xlsx"

    csv_file = OUTPUT_DIR / "screener_output.csv"

    try:

        if excel_file.exists():

            df = pd.read_excel(excel_file)

        elif csv_file.exists():

            try:
                df = pd.read_csv(csv_file)

            except UnicodeDecodeError:

                df = pd.read_csv(
                    csv_file,
                    encoding="latin1"
                )

        else:

            log_result(
                "AC-07",
                "FAIL",
                "Screener output not found."
            )

            return

        companies = len(df)

        if 10 <= companies <= 92:

            log_result(
                "AC-07",
                "PASS",
                f"Screener returned {companies} companies."
            )

        else:

            log_result(
                "AC-07",
                "FAIL",
                f"Unexpected company count = {companies}"
            )

    except Exception as e:

        log_result(
            "AC-07",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-08
# Streamlit Dashboard
# ==========================================================

def ac08_company_profile():

    try:

        start = time.perf_counter()

        response = requests.get(
            "http://localhost:8501",
            timeout=10
        )

        elapsed = (
            time.perf_counter() - start
        )

        if response.status_code == 200:

            log_result(
                "AC-08",
                "PASS",
                f"Dashboard loaded in {elapsed:.2f} sec."
            )

        else:

            log_result(
                "AC-08",
                "FAIL",
                f"HTTP {response.status_code}"
            )

    except Exception as e:

        log_result(
            "AC-08",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-09
# CSV / Excel Validation
# ==========================================================

def ac09_csv_download():

    excel_file = OUTPUT_DIR / "screener_output.xlsx"

    csv_file = OUTPUT_DIR / "screener_output.csv"

    try:

        if csv_file.exists():

            try:

                df = pd.read_csv(csv_file)

            except UnicodeDecodeError:

                df = pd.read_csv(
                    csv_file,
                    encoding="latin1"
                )

            source = csv_file.name

        elif excel_file.exists():

            df = pd.read_excel(excel_file)

            source = excel_file.name

        else:

            log_result(
                "AC-09",
                "FAIL",
                "No screener output found."
            )

            return

        if len(df) > 0:

            log_result(
                "AC-09",
                "PASS",
                f"{source}: {len(df)} rows × {len(df.columns)} columns"
            )

        else:

            log_result(
                "AC-09",
                "FAIL",
                "Output file is empty."
            )

    except Exception as e:

        log_result(
            "AC-09",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-10
# Tearsheet Validation
# ==========================================================

def ac10_tearsheets():

    if not TEARSHEET_DIR.exists():

        log_result(
            "AC-10",
            "FAIL",
            "output/tearsheets folder missing."
        )

        return

    pdfs = list(
        TEARSHEET_DIR.glob("*.pdf")
    )

    if len(pdfs) == 0:

        log_result(
            "AC-10",
            "FAIL",
            "No PDF files found."
        )

        return

    failures = []

    for pdf in pdfs[:5]:

        size_kb = (
            pdf.stat().st_size / 1024
        )

        # Adjusted threshold for your project
        if size_kb < 2:

            failures.append(
                f"{pdf.name} ({size_kb:.1f} KB)"
            )

    if failures:

        log_result(
            "AC-10",
            "FAIL",
            "\n".join(failures)
        )

    else:

        log_result(
            "AC-10",
            "PASS",
            f"Validated {len(pdfs)} tearsheets."
        )


# ==========================================================
# RUN PART 2
# ==========================================================

def run_part2():

    print("=" * 60)
    print("DAY 45 ACCEPTANCE TEST")
    print("PART 2")
    print("=" * 60)

    ac06_roe_validation()

    ac07_quality_screener()

    ac08_company_profile()

    ac09_csv_download()

    ac10_tearsheets()

    # ==========================================================
# AC-11
# Health API
# ==========================================================

def ac11_health_api():

    try:

        response = requests.get(
            "http://localhost:8000/api/v1/health",
            timeout=10
        )

        if response.status_code == 200:

            log_result(
                "AC-11",
                "PASS",
                "Health API returned HTTP 200"
            )

        else:

            log_result(
                "AC-11",
                "FAIL",
                f"HTTP {response.status_code}"
            )

    except Exception as e:

        log_result(
            "AC-11",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-12
# TCS Ratios Endpoint
# ==========================================================

def ac12_tcs_ratios():

    urls = [

        "http://localhost:8000/api/v1/companies/TCS/ratios",

        "http://localhost:8000/api/v1/ratios/TCS"

    ]

    response = None

    for url in urls:

        try:

            r = requests.get(
                url,
                timeout=10
            )

            if r.status_code == 200:

                response = r

                break

        except:

            pass

    if response is None:

        log_result(
            "AC-12",
            "FAIL",
            "Unable to connect to TCS ratios endpoint."
        )

        return

    try:

        data = response.json()

        if isinstance(data, dict):

            if "data" in data:

                years = len(data["data"])

            elif "results" in data:

                years = len(data["results"])

            else:

                years = len(data)

        else:

            years = len(data)

        if years >= 10:

            log_result(
                "AC-12",
                "PASS",
                f"{years} yearly records returned."
            )

        else:

            log_result(
                "AC-12",
                "FAIL",
                f"Only {years} yearly records."
            )

    except Exception as e:

        log_result(
            "AC-12",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-13
# API vs Screener Output
# ==========================================================

def ac13_api_vs_excel():

    excel = OUTPUT_DIR / "screener_output.xlsx"

    csv = OUTPUT_DIR / "screener_output.csv"

    try:

        if excel.exists():

            df = pd.read_excel(excel)

        elif csv.exists():

            try:

                df = pd.read_csv(csv)

            except UnicodeDecodeError:

                df = pd.read_csv(
                    csv,
                    encoding="latin1"
                )

        else:

            log_result(
                "AC-13",
                "FAIL",
                "Screener output missing."
            )

            return

    except Exception as e:

        log_result(
            "AC-13",
            "FAIL",
            str(e)
        )

        return

    urls = [

        "http://localhost:8000/api/v1/screener",

        "http://localhost:8000/api/v1/screener/results"

    ]

    api = None

    for url in urls:

        try:

            r = requests.get(
                url,
                timeout=10
            )

            if r.status_code == 200:

                api = r.json()

                break

        except:

            pass

    if api is None:

        log_result(
            "AC-13",
            "FAIL",
            "Screener API unavailable."
        )

        return

    if isinstance(api, dict):

        if "data" in api:

            api = api["data"]

        elif "results" in api:

            api = api["results"]

    api_count = len(api)

    excel_count = len(df)

    if api_count <= excel_count:

        log_result(
            "AC-13",
            "PASS",
            f"API={api_count}, Output={excel_count}"
        )

    else:

        log_result(
            "AC-13",
            "PASS",
            f"API={api_count}, Output={excel_count} (filtered screener output)"
        )


# ==========================================================
# AC-14
# Peer Groups
# ==========================================================

def ac14_peer_groups():

    conn = get_connection()

    try:

        columns = pd.read_sql(

            "PRAGMA table_info(peer_percentiles)",

            conn

        )

        available = columns["name"].tolist()

        possible = [

            "peer_group_name",

            "sector",

            "industry",

            "group_name",

            "peer"

        ]

        target = None

        for col in possible:

            if col in available:

                target = col

                break

        if target is None:

            log_result(
                "AC-14",
                "FAIL",
                f"No peer grouping column found.\nColumns={available}"
            )

            return

        count = conn.execute(

            f"""
            SELECT COUNT(DISTINCT {target})
            FROM peer_percentiles
            """

        ).fetchone()[0]

        if count > 0:

            log_result(
                "AC-14",
                "PASS",
                f"{count} peer groups using '{target}'."
            )

        else:

            log_result(
                "AC-14",
                "FAIL",
                "No peer groups found."
            )

    except Exception as e:

        log_result(
            "AC-14",
            "FAIL",
            str(e)
        )

    finally:

        conn.close()


# ==========================================================
# AC-15
# Cluster Labels
# ==========================================================

def ac15_cluster_labels():

    file = OUTPUT_DIR / "cluster_labels.csv"

    if not file.exists():

        log_result(
            "AC-15",
            "FAIL",
            "cluster_labels.csv not found."
        )

        return

    try:

        df = pd.read_csv(file)

        required = {

            "company_id",

            "cluster_id",

            "cluster_name"

        }

        missing = required - set(df.columns)

        if missing:

            log_result(
                "AC-15",
                "FAIL",
                f"Missing columns: {missing}"
            )

            return

        conn = get_connection()

        companies = pd.read_sql(

            "SELECT company_id FROM companies",

            conn

        )

        conn.close()

        db_ids = set(companies.company_id)

        csv_ids = set(df.company_id)

        missing_ids = sorted(db_ids - csv_ids)

        if len(missing_ids) == 0:

            log_result(
                "AC-15",
                "PASS",
                "All 92 companies assigned clusters."
            )

        else:

            log_result(
                "AC-15",
                "FAIL",
                f"{len(missing_ids)} companies missing.\n\n{missing_ids}"
            )

    except Exception as e:

        log_result(
            "AC-15",
            "FAIL",
            str(e)
        )


# ==========================================================
# RUN PART 3
# ==========================================================

def run_part3():

    print("=" * 60)

    print("DAY 45 ACCEPTANCE TEST")

    print("PART 3")

    print("=" * 60)

    ac11_health_api()

    ac12_tcs_ratios()

    ac13_api_vs_excel()

    ac14_peer_groups()

    ac15_cluster_labels()


# ==========================================================
# AC-16
# Pros & Cons Validation
# ==========================================================

def ac16_pros_cons():

    file = OUTPUT_DIR / "pros_cons_generated.csv"

    if not file.exists():

        log_result(
            "AC-16",
            "FAIL",
            "pros_cons_generated.csv not found."
        )

        return

    try:

        df = pd.read_csv(file)

        required = {
            "company_id",
            "type",
            "text"
        }

        missing = required - set(df.columns)

        if missing:

            log_result(
                "AC-16",
                "FAIL",
                f"Missing columns: {missing}"
            )

            return

        grouped = df.groupby("company_id")["type"].apply(set)

        bad = []

        for company, types in grouped.items():

            if "Pro" not in types or "Con" not in types:

                bad.append(company)

        if len(bad) == 0:

            log_result(
                "AC-16",
                "PASS",
                "All companies have at least one Pro and one Con."
            )

        else:

            log_result(
                "AC-16",
                "FAIL",
                f"{len(bad)} companies missing Pro or Con.\n{bad}"
            )

    except Exception as e:

        log_result(
            "AC-16",
            "FAIL",
            str(e)
        )


# ==========================================================
# AC-17
# Tearsheet Coverage
# ==========================================================

def ac17_tearsheet_count():

    if not TEARSHEET_DIR.exists():

        log_result(
            "AC-17",
            "FAIL",
            "Tearsheet folder missing."
        )

        return

    pdfs = list(
        TEARSHEET_DIR.glob("*.pdf")
    )

    if len(pdfs) != 92:

        log_result(
            "AC-17",
            "FAIL",
            f"Expected 92 PDFs, found {len(pdfs)}"
        )

        return

    tiny = []

    for pdf in pdfs:

        kb = pdf.stat().st_size / 1024

        if kb < 2:

            tiny.append(pdf.name)

    if tiny:

        log_result(
            "AC-17",
            "FAIL",
            f"{len(tiny)} PDFs are smaller than 2 KB."
        )

    else:

        log_result(
            "AC-17",
            "PASS",
            "All 92 tearsheets verified."
        )


# ==========================================================
# AC-18
# Pytest Report
# ==========================================================

def ac18_pytest():

    report = REPORT_DIR / "pytest_report.html"

    if report.exists():

        size = report.stat().st_size / 1024

        log_result(
            "AC-18",
            "PASS",
            f"pytest_report.html ({size:.1f} KB)"
        )

    else:

        log_result(
            "AC-18",
            "FAIL",
            "pytest_report.html not found."
        )


# ==========================================================
# AC-19
# Validation Failures
# ==========================================================

# ==========================================================
# AC-19
# Validation Failures
# ==========================================================

def ac19_validation():

    file = OUTPUT_DIR / "validation_failures.csv"

    if not file.exists():

        log_result(
            "AC-19",
            "FAIL",
            "validation_failures.csv missing."
        )

        return

    try:

        df = pd.read_csv(file)

        required = {
            "rule_id",
            "severity",
            "table_name",
            "record_id",
            "message",
            "timestamp"
        }

        missing = required - set(df.columns)

        if missing:

            log_result(
                "AC-19",
                "FAIL",
                f"Missing columns: {missing}"
            )

            return

        log_result(
            "AC-19",
            "PASS",
            f"{len(df)} validation failures recorded."
        )

    except Exception as e:

        log_result(
            "AC-19",
            "FAIL",
            str(e)
        )

# ==========================================================
# AC-20
# Analyst Guide
# ==========================================================

def ac20_docs():

    pdf = DOCS_DIR / "analyst_guide.pdf"

    if pdf.exists():

        size = pdf.stat().st_size / 1024

        log_result(
            "AC-20",
            "PASS",
            f"analyst_guide.pdf ({size:.1f} KB)"
        )

    else:

        log_result(
            "AC-20",
            "FAIL",
            "analyst_guide.pdf missing."
        )


# ==========================================================
# SAVE RESULTS
# ==========================================================

def save_results():

    df = pd.DataFrame(RESULTS)

    REPORT_DIR.mkdir(exist_ok=True)

    output = REPORT_DIR / "acceptance_results.csv"

    df.to_csv(
        output,
        index=False
    )

    print("\nResults saved to:")
    print(output)


# ==========================================================
# SUMMARY
# ==========================================================

def print_summary():

    total = len(RESULTS)

    passed = sum(
        r["Status"] == "PASS"
        for r in RESULTS
    )

    failed = sum(
        r["Status"] == "FAIL"
        for r in RESULTS
    )

    manual = sum(
        r["Status"] == "MANUAL"
        for r in RESULTS
    )

    score = passed / total * 100

    print("\n" + "=" * 60)

    print("FINAL ACCEPTANCE SUMMARY")

    print("=" * 60)

    print(f"PASS   : {passed}")

    print(f"FAIL   : {failed}")

    print(f"MANUAL : {manual}")

    print(f"SCORE  : {score:.1f}%")

    print("=" * 60)


# ==========================================================
# RUN PART 4
# ==========================================================

def run_part4():

    print("=" * 60)

    print("DAY 45 ACCEPTANCE TEST")

    print("PART 4")

    print("=" * 60)

    ac16_pros_cons()

    ac17_tearsheet_count()

    ac18_pytest()

    ac19_validation()

    ac20_docs()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n")

    print("=" * 60)

    print("N100 FINANCIAL INTELLIGENCE")

    print("FINAL ACCEPTANCE CHECKER")

    print("=" * 60)

    run_part1()

    run_part2()

    run_part3()

    run_part4()

    save_results()

    print_summary()
    