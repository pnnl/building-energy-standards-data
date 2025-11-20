import json
import sqlite3
from pathlib import Path
from langchain_core.documents import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def load_schema_docs(json_path: str, sqlite_path: str):
    data = json.loads(Path(json_path).read_text())
    field_desc = data.get("field descriptions", {})
    table_desc = data.get("table descriptions", {})

    docs = []

    # --- Extract SQL schema from SQLite ---
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        rows = cursor.fetchall()

        # columns = [r[1] for r in rows]  # r[1] is column name
        # ddl_rows = "\n".join(str(r) for r in rows)

        # docs.append(
        #     Document(
        #         page_content=f"TABLE: {table}\nCOLUMNS: {columns}\nRAW: {ddl_rows}",
        #         metadata={"type": "table", "table": table},
        #     )
        # )

        # Add column-level docs
        for r in rows:
            col_name = r[1]
            col_type = r[2]

            description = field_desc.get(col_name, "No description available.")

            docs.append(
                Document(
                    page_content=(
                        f"FIELD: {col_name}\n"
                        f"TABLE: {table}\n"
                        f"TYPE: {col_type}\n"
                        f"DESCRIPTION: {description}"
                    ),
                    metadata={"type": "field", "table": table, "field": col_name},
                )
            )

    # Add JSON table descriptions if present
    for table, description in table_desc.items():
        docs.append(
            Document(
                page_content=f"TABLE NAME: {table}\nDESCRIPTION: {description}",
                metadata={"type": "table_desc", "table": table},
            )
        )

    conn.close()
    return docs


# MPNet embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Load your schema documents
docs = load_schema_docs("database_docs/doc_base.json", "openstudio_standards.db")

# Create / load Chroma DB
db = Chroma.from_documents(
    docs,
    embedding,
    collection_name="osstd_db_schema_rag",
    persist_directory="fine_tuning/rag/db",
)