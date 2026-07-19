"""
Sprint 5 - Day 33

Company Tearsheet Generator
"""

import sqlite3
from pathlib import Path
from turtle import color

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# =====================================================
# PROJECT PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

TEARSHEET_DIR = OUTPUT_DIR / "tearsheets"
TEARSHEET_DIR.mkdir(exist_ok=True)

# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# LOAD DATABASE
# =====================================================

def load_database():

    conn = get_connection()

    data = {

        "companies":
            pd.read_sql(
                "SELECT * FROM companies",
                conn
            ),

        "financial_ratios":
            pd.read_sql(
                "SELECT * FROM financial_ratios",
                conn
            ),

        "cash_flow":
            pd.read_sql(
                "SELECT * FROM cash_flow",
                conn
            ),

        "profit_loss":
            pd.read_sql(
                "SELECT * FROM profit_loss",
                conn
            ),

        "balance_sheet":
            pd.read_sql(
                "SELECT * FROM balance_sheet",
                conn
            )
    }

    conn.close()

    return data


# =====================================================
# LOAD ANALYTICS OUTPUTS
# =====================================================

def load_outputs():

    outputs = {

        "analysis":
            pd.read_csv(
                OUTPUT_DIR / "analysis_parsed.csv"
            ),

        "pros_cons":
            pd.read_csv(
                OUTPUT_DIR / "pros_cons_generated.csv"
            ),

        "cashflow":
            pd.read_excel(
                OUTPUT_DIR / "cashflow_intelligence.xlsx"
            ),

        "capital":
            pd.read_excel(
                OUTPUT_DIR / "capital_allocation_report.xlsx"
            )
    }

    return outputs


# =====================================================
# PREVIEW
# =====================================================

def preview():

    db = load_database()

    outputs = load_outputs()

    print("=" * 60)
    print("Company Tearsheet Generator")
    print("=" * 60)

    print("\nDatabase Tables\n")

    for name, df in db.items():
        print(f"{name:<20}: {len(df)} rows")

    print("\nGenerated Analytics\n")

    for name, df in outputs.items():
        print(f"{name:<20}: {len(df)} rows")

    pros = outputs["pros_cons"]

    print(pros.head())
    print(pros.columns.tolist())
# =====================================================
# BUILD COMPANY DATASET
# =====================================================

def build_company_dataset():

    db = load_database()
    outputs = load_outputs()

    companies = db["companies"]

    ratios = (
        db["financial_ratios"]
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    cashflow = outputs["cashflow"]

    capital = outputs["capital"]

    analysis = (
        outputs["analysis"]
        .pivot_table(
            index="company_id",
            columns="metric",
            values="value",
            aggfunc="first"
        )
        .reset_index()
    )

    # =====================================================
    # BUILD PROS & CONS SUMMARY
    # =====================================================

    pros_cons = outputs["pros_cons"]

    pros = (
        pros_cons[pros_cons["type"] == "Pro"]
        .groupby("company_id")["text"]
        .apply(lambda x: "\n".join(x.head(5)))
        .reset_index(name="pros")
    )

    cons = (
        pros_cons[pros_cons["type"] == "Con"]
        .groupby("company_id")["text"]
        .apply(lambda x: "\n".join(x.head(5)))
        .reset_index(name="cons")
    )

    pros = pros.merge(
        cons,
        on="company_id",
        how="outer"
    )

    dataset = (
        companies
        .merge(
            ratios,
            on="company_id",
            how="left"
        )
        .merge(
            cashflow,
            on="company_id",
            how="left"
        )
        .merge(
            capital,
            on="company_id",
            how="left"
        )
        .merge(
            analysis,
            on="company_id",
            how="left"
        )
        .merge(
            pros,
            on="company_id",
            how="left"
        )
    )

    print("\n" + "=" * 60)
    print("Unified Company Dataset")
    print("=" * 60)

    print(f"Companies : {len(dataset)}")

    print("\nColumns")

    print(dataset.columns.tolist())

    return dataset


# =====================================================
# BUILD TEARSHEET DATA
# =====================================================

def build_tearsheet_data(company_id, dataset):

    row = dataset.loc[
        dataset["company_id"] == company_id
    ]

    if row.empty:
        return None

    row = row.iloc[0]

    tearsheet = {

        # Company Profile
        "company_id": row["company_id"],
        "company_name": row.get("company_name", row.get("company_name_x")),
        "sector": row.get("sector", ""),
        "website": row.get("website", ""),
        "logo": row.get("company_logo", ""),

        # Valuation
        "market_cap": row.get("market_cap_crore", 0),
        "pe": row.get("pe_ratio", 0),
        "pb": row.get("pb_ratio", 0),
        "ev_ebitda": row.get("ev_ebitda", 0),
        "dividend_yield": row.get("dividend_yield_pct", 0),

        # Quality
        "roe": row.get("roe_percentage", row.get("ROE", 0)),
        "roce": row.get("roce_percentage", 0),

        # Growth
        "sales_growth": row.get("Sales Growth", ""),
        "profit_growth": row.get("Profit Growth", ""),
        "stock_cagr": row.get("Stock CAGR", ""),

        # Cash Flow
        "cfo_quality": row.get("cfo_quality_label", ""),
        "fcf_cagr": row.get("fcf_cagr_5yr", 0),
        "capital_pattern": row.get("capital_allocation_label", ""),

        # Capital Allocation
        "capital_score": row.get("capital_score", 0),
        "rating": row.get("rating", ""),
        "reinvestment": row.get("reinvestment_category", ""),
        "debt_trend": row.get("debt_trend", ""),
        "leverage": row.get("leverage", ""),

        # AI Insights
        "pros": row.get("pros", ""),
        "cons": row.get("cons", ""),

        # Description
        "about": row.get("about_company", "")
    }

    return tearsheet

def preview_tearsheet(dataset):

    company = dataset.iloc[0]["company_id"]

    ts = build_tearsheet_data(company, dataset)

    print("\n" + "=" * 60)
    print("Sample Tearsheet Data")
    print("=" * 60)

    for key, value in ts.items():
        print(f"{key:<20}: {value}")

# =====================================================
# SAFE TEXT
# =====================================================

def safe_text(value, default="Not Available"):

    if pd.isna(value):
        return default

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return default

    return value.replace("\n", "<br/>")

# =====================================================
# PROFESSIONAL PDF TEARSHEET
# =====================================================

def generate_tearsheet_pdf(tearsheet):

    pdf_path = TEARSHEET_DIR / f"{tearsheet['company_id']}.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = HexColor("#0B5394")

    heading_style = styles["Heading2"]
    heading_style.textColor = HexColor("#1F4E79")

    normal = styles["BodyText"]

    story = []

    # =====================================================
    # HEADER
    # =====================================================

    story.append(
        Paragraph(
            f"<b>{safe_text(tearsheet['company_name'], 'Unknown Company')}</b>",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Investment Rating :</b> {safe_text(tearsheet['rating'])}",
            heading_style
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    # =====================================================
    # COMPANY OVERVIEW
    # =====================================================

    story.append(
        Paragraph(
            "<b>Company Overview</b>",
            heading_style
        )
    )

    overview = [
        ["Website", tearsheet["website"]],
        ["Sector", str(tearsheet["sector"])],
        ["Market Cap", f"{tearsheet['market_cap']:,.2f} Cr"],
        ["PE Ratio", tearsheet["pe"]],
        ["PB Ratio", tearsheet["pb"]],
        ["Dividend Yield", f"{tearsheet['dividend_yield']} %"],
    ]

    table = Table(
        overview,
        colWidths=[2.2 * inch, 4 * inch]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#D9EAF7")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(table)

    story.append(Spacer(1, 0.25 * inch))

    # =====================================================
    # FINANCIAL QUALITY
    # =====================================================

    story.append(
        Paragraph(
            "<b>Financial Quality</b>",
            heading_style
        )
    )

    quality = [
        ["ROE", tearsheet["roe"]],
        ["ROCE", tearsheet["roce"]],
        ["CFO Quality", tearsheet["cfo_quality"]],
        ["FCF CAGR", f"{tearsheet['fcf_cagr']:.2f}%"],
        ["Capital Pattern", tearsheet["capital_pattern"]],
    ]

    quality_table = Table(
        quality,
        colWidths=[2.2 * inch, 4 * inch]
    )

    quality_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#EAF4E2")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ])
    )

    story.append(quality_table)

    story.append(Spacer(1, 0.25 * inch))

    # =====================================================
    # CAPITAL ALLOCATION
    # =====================================================

    story.append(
        Paragraph(
            "<b>Capital Allocation</b>",
            heading_style
        )
    )

    capital = [
        ["Capital Score", tearsheet["capital_score"]],
        ["Reinvestment", tearsheet["reinvestment"]],
        ["Debt Trend", tearsheet["debt_trend"]],
        ["Leverage", tearsheet["leverage"]],
    ]

    capital_table = Table(
        capital,
        colWidths=[2.2 * inch, 4 * inch]
    )

    capital_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#FFF4CC")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ])
    )

    story.append(capital_table)

    story.append(Spacer(1, 0.25 * inch))

    # =====================================================
    # BUSINESS OVERVIEW
    # =====================================================

    story.append(
        Paragraph(
            "<b>Business Overview</b>",
            heading_style
        )
    )

    story.append(
        Paragraph(
            safe_text(
                tearsheet["about"],
                "Business description not available."
            ),
            normal
        )
    )

    story.append(Spacer(1, 0.20 * inch))

    # =====================================================
    # STRENGTHS
    # =====================================================

    story.append(
        Paragraph(
            "<b>Strengths</b>",
            heading_style
        )
    )

    story.append(
        Paragraph(
            safe_text(
                tearsheet["pros"],
                "No major strengths identified."
            ),
            normal
        )
    )

    story.append(Spacer(1, 0.20 * inch))

    # =====================================================
    # RISKS
    # =====================================================

    story.append(
        Paragraph(
            "<b>Risks</b>",
            heading_style
        )
    )

    story.append(
        Paragraph(
            safe_text(
                tearsheet["cons"],
                "No major risks identified."
            ),
            normal
        )
    )

    doc.build(story)

    print(f"PDF Generated : {pdf_path}")

    return pdf_path

# =====================================================
# BATCH PDF GENERATION
# =====================================================

def generate_all_tearsheets(dataset):

    print("\n" + "=" * 60)
    print("Generating Company Tearsheets")
    print("=" * 60)

    generated = []
    failed = []

    for company_id in sorted(dataset["company_id"].unique()):

        try:
            tearsheet = build_tearsheet_data(company_id, dataset)

            if tearsheet is None:
                failed.append(company_id)
                continue

            generate_tearsheet_pdf(tearsheet)

            generated.append(company_id)

        except Exception as e:
            print(f"❌ {company_id} : {e}")
            failed.append(company_id)

    print("\n" + "=" * 60)
    print("Generation Summary")
    print("=" * 60)

    print(f"Generated : {len(generated)}")
    print(f"Failed    : {len(failed)}")

    if failed:
        print("\nFailed Companies:")
        print(failed)

    return generated, failed


# =====================================================
# EXPORT SUMMARY
# =====================================================

def export_tearsheet_summary(generated, failed):

    summary = pd.DataFrame({
        "metric": [
            "Total Companies",
            "Generated",
            "Failed"
        ],
        "value": [
            len(generated) + len(failed),
            len(generated),
            len(failed)
        ]
    })

    failed_df = pd.DataFrame({
        "failed_company": failed
    })

    summary.to_csv(
        OUTPUT_DIR / "tearsheet_summary.csv",
        index=False
    )

    failed_df.to_csv(
        OUTPUT_DIR / "tearsheet_failures.csv",
        index=False
    )

    print("\nSummary Saved")

    print(OUTPUT_DIR / "tearsheet_summary.csv")
    print(OUTPUT_DIR / "tearsheet_failures.csv")

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    preview()

    dataset = build_company_dataset()

    generated, failed = generate_all_tearsheets(dataset)

    export_tearsheet_summary(generated, failed)