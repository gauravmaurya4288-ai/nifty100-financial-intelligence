"""
SQLite database connection utilities.
"""

import sqlite3
from contextlib import contextmanager

from .config import DB_PATH


@contextmanager
def get_connection():
    """
    Return SQLite database connection.
    """

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    try:
        yield conn

    finally:
        conn.close()


def execute_query(query: str, params: tuple = ()):
    """
    Execute SELECT query.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        columns = [c[0] for c in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

def execute_scalar(query):
    """
    Execute scalar query.
    """

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(query)

        row = cursor.fetchone()

        if row:
            return row[0]

        return None