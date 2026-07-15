import sqlite3

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

with open("db/create_annual_reports.sql","r") as f:
    conn.executescript(f.read())

conn.commit()

print("Annual Reports table created successfully.")

conn.close()