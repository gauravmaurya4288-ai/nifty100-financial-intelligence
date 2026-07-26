from src.api.database import execute_query

sql = """
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
"""

tables = execute_query(sql)

print("\n===== DATABASE TABLES =====\n")

for table in tables:
    print(table["name"])



from src.api.database import execute_query

table_name = "companies"

sql = f"""
PRAGMA table_info({table_name});
"""

columns = execute_query(sql)

print(f"\n===== {table_name.upper()} =====\n")

for column in columns:
    print(column)


from src.api.database import execute_query

tables = execute_query("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

for table in tables:

    table_name = table["name"]

    print("\n" + "=" * 60)
    print(table_name.upper())
    print("=" * 60)

    columns = execute_query(
        f"PRAGMA table_info({table_name});"
    )

    for col in columns:
        print(col)

    from src.api.database import execute_query

table_name = "companies"

sql = f"""
SELECT *
FROM {table_name}
LIMIT 5;
"""

rows = execute_query(sql)

print(rows)

from src.api.database import execute_query

tables = execute_query("""
SELECT name
FROM sqlite_master
WHERE type='table';
""")

print("\n===== TABLE ROW COUNTS =====\n")

for table in tables:

    table_name = table["name"]

    sql = f"""
    SELECT COUNT(*) AS total
    FROM {table_name};
    """

    count = execute_query(sql)

    print(f"{table_name:<30} {count[0]['total']}")

from src.api.database import execute_query

sql = """
SELECT
    name,
    sql
FROM sqlite_master
WHERE type='table'
ORDER BY name;
"""

tables = execute_query(sql)

for table in tables:

    print("\n" + "=" * 80)
    print(table["name"])
    print("=" * 80)

    print(table["sql"])

from src.api.database import execute_query

print("SQLite Version")
print(execute_query("SELECT sqlite_version() AS version;"))

print("\nPage Count")
print(execute_query("PRAGMA page_count;"))

print("\nPage Size")
print(execute_query("PRAGMA page_size;"))


from src.api.database import execute_query

sql = """
SELECT
    name,
    tbl_name
FROM sqlite_master
WHERE type='index'
ORDER BY tbl_name;
"""

indexes = execute_query(sql)

for index in indexes:
    print(index)


