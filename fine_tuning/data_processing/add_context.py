import pandas as pd
import re
import sqlite3

# ---------- CONFIG ----------
EXCEL_FILE = "fine_tuning/dataset/raw/building_std_queries.xlsx"
OUTPUT_FILE = "fine_tuning/dataset/processed/questions_with_context.csv"
DB_FILE = "openstudio_standards.db"

# ---------- LOAD EXCEL ----------
df = pd.read_excel(EXCEL_FILE)

# ---------- CONNECT TO SQLITE ----------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Build a dictionary of table_name -> CREATE TABLE statement
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

table_schemas = {name: sql for name, sql in tables}
print(table_schemas)

# ---------- FUNCTIONS ----------
def extract_table_names(sql):
    """Extract all table names from a SQL SELECT statement."""
    # Matches FROM table_name or JOIN table_name
    matches = re.findall(r'(?:FROM|JOIN)\s+([^\s,;]+)', sql, re.IGNORECASE)
    return matches

def get_table_schema(table_names):
    """Return the CREATE TABLE statements for the given tables."""
    schemas = []
    for table_name in table_names:
        schema = table_schemas.get(table_name)
        if schema:
            schemas.append(schema)
        else:
            schemas.append(f"Schema not found for table: {table_name}")
    return "; ".join(schemas)

def generate_context(sql):
    table_names = extract_table_names(sql)
    if table_names:
        return get_table_schema(table_names)
    return None

df['context'] = df['answer'].apply(generate_context)

# ---------- SAVE TO NEW CSV ----------
df = df[["answer", "question", "context"]]
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved updated csv to {OUTPUT_FILE}")

# ---------- CLOSE DB ----------
conn.close()
