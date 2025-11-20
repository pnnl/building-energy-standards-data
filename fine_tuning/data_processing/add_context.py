import pandas as pd
import re
import sqlite3

# ---------- CONFIG ----------
EXCEL_FILE = "fine_tuning/dataset/raw/building_std_queries.xlsx"
OUTPUT_FILE = "fine_tuning/dataset/processed/questions_with_context.csv"
DB_FILE = "openstudio_standards.db"

def clean_create_table(sql):
    """
    Clean the CREATE TABLE statement by:
    - Removing excessive whitespace
    - Removing column types and constraints, keep only column names
    - Removing extra table options (like WITHOUT ROWID)
    """
    # Extract table name and column defs
    m = re.match(r"CREATE TABLE\s+(\S+)\s*\((.*)\)", sql, re.DOTALL | re.IGNORECASE)
    if not m:
        return sql.strip()
    table_name, cols = m.groups()

    # Split columns by comma, handle multi-line and possible commas inside constraints
    col_defs = []
    depth = 0
    current_col = ""
    for char in cols:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            col_defs.append(current_col.strip())
            current_col = ""
        else:
            current_col += char
    if current_col.strip():
        col_defs.append(current_col.strip())

    # Extract just column names (the first word before space)
    col_names = []
    for col_def in col_defs:
        # skip constraints like PRIMARY KEY or FOREIGN KEY (those usually start with those keywords)
        if re.match(r"^(PRIMARY|FOREIGN|UNIQUE|CHECK|CONSTRAINT)", col_def, re.IGNORECASE):
            continue
        # extract first word as column name
        col_name = col_def.split()[0]
        col_names.append(col_name)

    cleaned = f"{table_name} : {' , '.join(col_names)});"
    return cleaned


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

def add_context(dataset_path, db_path, output_path=None):
    # ---------- LOAD EXCEL ----------
    df = pd.read_excel(dataset_path)

    # ---------- CONNECT TO SQLITE ----------
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build a dictionary of table_name -> CREATE TABLE statement
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_schemas = {name: sql for name, sql in tables}

    # ---------- FUNCTIONS ----------
    def extract_table_names(sql):
        """Extract all table names from a SQL SELECT statement."""
        # Matches FROM table_name or JOIN table_name, strip quotes if any
        matches = re.findall(r"(?:FROM|JOIN)\s+['\"]?([^\s,;'\"()]+)['\"]?", sql, re.IGNORECASE)
        # Deduplicate and preserve order
        seen = set()
        tables = []
        for t in matches:
            if t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    def get_table_context(table_names):
        """Return cleaned CREATE TABLE statements and sample rows for given tables."""
        contexts = []
        for table_name in table_names:
            schema = table_schemas.get(table_name)
            if schema:
                cleaned_schema = clean_create_table(schema)
                sample_rows = get_sample_rows(conn, table_name)
                context_piece = f"{cleaned_schema}\nSample rows:\n{sample_rows}"
                contexts.append(context_piece)
        return "\n\n".join(contexts)

    def generate_context(sql):
        table_names = extract_table_names(sql)
        if table_names:
            return get_table_context(table_names)
        return None

    df["context"] = df["answer"].apply(generate_context)

    # Include only relevant columns in output
    df = df[["answer", "question", "context"]]

    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Saved updated csv to {output_path}")

    conn.close()

    return df


if __name__ == "__main__":
    add_context(EXCEL_FILE, DB_FILE, OUTPUT_FILE)
