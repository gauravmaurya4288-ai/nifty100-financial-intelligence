import sqlite3

conn = sqlite3.connect(
    "db/nifty100.db"
)

conn.execute(
    "PRAGMA foreign_keys = ON;"
)

with open(
    "db/schema.sql",
    "r"
) as f:

    conn.executescript(
        f.read()
    )

conn.commit()
conn.close()

print(
    "Database Created Successfully"
)