import sqlite3
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))
from src.screener.presets import (
    quality_compounder,
    value_pick,
    growth_accelerator,
    dividend_champion,
    debt_free_bluechip,
    turnaround_watch,
    summary
)

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

df = pd.read_sql(

    "SELECT * FROM financial_ratios",

    conn

)

print(df.shape)

quality = quality_compounder(df)

value = value_pick(df)

growth = growth_accelerator(df)

dividend = dividend_champion(df)

bluechip = debt_free_bluechip(df)

turnaround = turnaround_watch(df)



print("="*60)

print("Quality Compounder :", len(quality))

print("Value Pick :", len(value))

print("Growth Accelerator :", len(growth))

print("Dividend Champion :", len(dividend))

print("Debt Free Bluechip :", len(bluechip))

print("Turnaround Watch :", len(turnaround))

OUTPUT = "output/screener_output.xlsx"

with pd.ExcelWriter(

    OUTPUT,

    engine="openpyxl"

) as writer:

    quality.to_excel(

        writer,

        sheet_name="Quality Compounder",

        index=False

    )

    value.to_excel(

        writer,

        sheet_name="Value Pick",

        index=False

    )

    growth.to_excel(

        writer,

        sheet_name="Growth Accelerator",

        index=False

    )

    dividend.to_excel(

        writer,

        sheet_name="Dividend Champion",

        index=False

    )

    bluechip.to_excel(

        writer,

        sheet_name="Debt Free Bluechip",

        index=False

    )

    turnaround.to_excel(

        writer,

        sheet_name="Turnaround Watch",

        index=False

    )

print()

print("Excel Generated Successfully")

conn.close()