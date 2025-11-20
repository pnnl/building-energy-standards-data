import json
import sqlite3
from pathlib import Path
from langchain_core.documents import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

db = Chroma(
    collection_name="osstd_db_schema_rag",
    persist_directory="fine_tuning/rag/db",
    embedding_function=embedding,
)

query = "Maximum permitted solar heat coefficient for a southern facing nonresidential glass door in Climate Zone 7 according to ASHRAE 90.1-2004?"

table_retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5, "filter": {"type": "table_desc"}},
)

table_docs = table_retriever.get_relevant_documents(query)

# field_retriever = db.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 4, "filter": {"table": f"{table_docs[0].metadata["table"]}"}},
# )

# field_docs = field_retriever.get_relevant_documents(query)

results = table_docs

for i, r in enumerate(table_docs):
    print(f"\n=== RESULT {i} ===")
    print(r.page_content)
    print(r.metadata)
