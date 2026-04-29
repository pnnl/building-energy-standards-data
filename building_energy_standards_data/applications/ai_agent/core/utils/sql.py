import sqlite3
from typing import Any, Dict, List
import re
import pandas as pd



def extract_select_query(query: str) -> str:
    """
    Extract everything starting from the first SELECT (case-insensitive).
    Raises ValueError if no SELECT is found.
    """
    match = re.search(r"\bselect\b", query, re.IGNORECASE)
    if not match:
        raise ValueError("No SELECT statement found in query.")
    query = query[match.start():]
    query = re.sub(r"\n?```+\s*$", "", query)
    return query

def run_sqlite_query(
    query: str,
    conn
) -> List[Dict[str, Any]]:
    query = extract_select_query(query)
    conn.row_factory = sqlite3.Row

    try:
        with conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []


def get_sample_rows(conn, table_name, max_rows=3):
    """
    Fetch a few random sample rows from the table and format as CSV-like string without headers.
    """
    try:
        query = f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {max_rows};"
        df_sample = pd.read_sql_query(query, conn)
        if df_sample.empty:
            return "No sample rows."
        else:
            return df_sample.to_csv(index=False, header=False).strip()
    except Exception as e:
        return f"Could not fetch sample rows: {e}"
