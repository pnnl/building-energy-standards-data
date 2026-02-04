from fine_tuning.find_table.table_metadata import SchemaMetadataService
from fine_tuning.find_table.table_parser import TableParser
from fine_tuning.find_table.types import *
from fine_tuning.data_processing.add_context import get_sample_rows
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
import sqlite3

from typing import Any, Dict, List, Optional, Type
import requests
import json
from pathlib import Path
import re
from langchain_core.documents import Document

from langchain_chroma import Chroma

TOP_K = 3


def cosine_similarity(a, b):
    return np.dot(a, b)  # embeddings normalized so dot product = cosine similarity


def generate(prompt):
    url = "http://rc-chat.pnl.gov:11434/v1/completions"  # or your actual API endpoint

    payload = {
        "model": "llama3.3:70b",
        "prompt": prompt,
        "top_p": 0.9,
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()

    generated_text = data["choices"][0]["text"].strip()
    return generated_text


def enum_values(enum_class: Type[StrEnum]):
    return [e.value for e in enum_class]


def extract_descriptor_attributes(query):
    prompt = f"""
    Extract the descriptor attributes from the following user query about building energy standards data. We are using this data to find a specific table in a database.

    User query:
    \"\"\"{query}\"\"\"

    Return a JSON object with the following fields:

    - domain (string or null): One of {enum_values(Domain) + [None]}. Represents the high-level area such as HVAC, envelope, support, etc.
    - topic (string or null): One of {enum_values(Topic) + [None]}. Describes the subject focus like minimum requirements, lighting data, or space types.
    - data_role (string or null): One of {enum_values(DataRole) + [None]}. Indicates the role of the data, e.g., requirements, reference_data, or normative_inputs.
    - classification_type (string or null): One of {enum_values(ClassificationType) + [None]}. Specifies the classification nature, like taxonomy or subclassification.
    - system (string or null): One of {enum_values(System) + [None]}. The specific system involved, such as motor, water_heater, lighting, etc.
    - sub_system (string or null): One of {enum_values(SubSystem) + [None]}. Further subdivision such as heating or cooling subsystems. This only applies to heat pumps.
    - standard_family (string or null): One of {enum_values(StandardFamily) + [None]}. The code or standard family. If necessary to answer query but not specified in the query, default to ASHRAE_90_1.
    - standard_year (integer four-digit year or null): The year of the applicable standard.
    - compliance_path (string or null): One of {enum_values(CompliancePath) + [None]}. The compliance method, such as "prescriptive" (default) or "appendix_g" which corresponds to tables with the "prm" suffix.

    Example output:
    {{
    "domain": "hvac",
    "topic": "minimum_requirements",
    "data_role": "requirements",
    "classification_type": null,
    "system": "motor",
    "sub_system": null,
    "standard_family": "ASHRAE_90_1",
    "standard_year": 2019,
    "compliance_path": "prescriptive"
    }}

    Do **not** include any other explanation, text, or formatting. Only output the JSON object.
    """

    resp = generate(prompt)
    return extract_json_from_text(resp)

def extract_json_from_text(text: str) -> dict | None:
    # Find the first {...} block
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def generate_json_table_descriptions(table_lookup_service: SchemaMetadataService):
    generated_descriptions = {}

    for table_name in table_lookup_service.get_table_names():
        table_descriptor = table_lookup_service.get_table_descriptor(table_name)
        columns_text = table_lookup_service.render_schema(table_lookup_service.get_schema(table_name))
        metadata_text = table_lookup_service.generate_metadata_text(table_descriptor, table_name=table_name, columns=columns_text)

        prompt = (
            f"Write a clear, 100-150 token, concise description for the database table named '{table_name}'. "
            "This database contains tabulated building energy standards data used in energy simulation and compliance evaluation. It includes key prescriptive requirements such as equipment efficiency and thermal performance assumptions, but does not cover all exceptions or nuanced code conditions. Use this context to write a clear, concise description for the following table."
            "Include the domain, system, and relevant standard or compliance path it supports. "
            "Describe the key data it holds, such as important columns and their role, including any date ranges, efficiency metrics, capacity limits, or annotations. "
            "Explain how this table is typically used to support compliance or reference within its context.\n\n"
            f"Here is the metadata:\n{metadata_text}"
        )

        generated_description = generate(prompt)
        generated_descriptions[table_name] = generated_description

    with open("generated_table_descriptions.json", "w") as f:
        json.dump(generated_descriptions, f, indent=2)

def get_table_descriptions():
    json_path = "fine_tuning/find_table/generated_table_descriptions.json"
    data = json.loads(Path(json_path).read_text())
    return data

def format_descriptor_attributes(attrs: dict) -> str:
    lines = []
    # Optional: if table key exists, print it first
    if "table" in attrs and attrs["table"]:
        lines.append(f"Table: {attrs['table']}")

    # Mapping keys to desired labels
    key_map = {
        "domain": "Domain",
        "topic": "Topic",
        "data_role": "Data role",
        "classification_type": "Classification type",
        "system": "System",
        "sub_system": "Sub-system",
        "standard_family": "Standard family",
        "standard_year": "Standard year",
        "compliance_path": "Compliance path",
    }

    for key, label in key_map.items():
        val = attrs.get(key)
        if val is None:
            val = "null"
        lines.append(f"{label}: {val}")

    return "\n".join(lines)

def parse_document(doc):
    """
    Parse a document string into a dictionary of {field: value},
    ignoring lines where value is 'Null' (case-insensitive).
    """
    field_values = {}
    for line in doc.strip().splitlines():
        if ':' in line:
            field, value = line.split(':', 1)
            field = field.strip()
            value = value.strip()
            if value.lower() != 'null':
                field_values[field] = value
    return field_values

def rank_documents(reference_doc, doc_list, top_k: int = TOP_K):
    """
    Rank documents by number of matching Field: Value pairs with reference_doc.
    Returns list of tuples (document, match_count), sorted descending by match_count.
    """
    ref_fields = parse_document(reference_doc)

    max_score = 0
    ranked = []
    for doc in doc_list:
        doc_fields = parse_document(doc)
        
        # Count matching field-value pairs
        shared_fields = ref_fields.keys() & doc_fields.keys()

        if not shared_fields:
            score = 0
        else:
            matches = sum(
                1 for f in shared_fields
                if ref_fields[f] == doc_fields[f]
            )
            score = matches / len(shared_fields)
            max_score = max(score, max_score)
        ranked.append((doc_fields["Table Name"], score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    max_ranking = ranked[0][1]
    ranked = [ranking for ranking in ranked if ranking[1] == max_ranking]

    return ranked

def llm_filter_tables(candidate_tables):
    table_descriptions = get_table_descriptions()

    candidate_tables_prompt = "\n\n".join(
        [f"Table: {t}\nDescription: {table_descriptions[t]}" for t in candidate_tables]
    )

    prompt = f"""
    Given the user query: "{query}"

    And the following candidate table descriptions:

    {candidate_tables_prompt}

    Please reply with only the database table name(s) necessary to answer the query.
    If multiple, separate them by commas. Do not add any other text.
    """
    
    # Step 5: Ask LLM for final table selection
    response = generate(prompt)
    
    table_names = [t.strip() for t in response.split(",") if t.strip()]

    return table_names

def llm_generate_sql(table_metadata: dict):
    filtered_table_info = "\n\n".join(table_metadata.values())

    prompt = f"""
    Use the following SQL tables:\n{filtered_table_info}
    
    Answer the user query by writing a SQL query:\n"{query}"

    Do not include an explanation.
    """

    print(prompt)

    response = generate(prompt)

    return response

def pipeline(query: str):
    """
    Idea: We can categorize the tables into having different attributes,
    and then find the closest matching table to a query by assigning the
    query the same attributes.
    """

    schema_metadata_service = SchemaMetadataService()

    # 1. Using LLM, extract 'descriptor' attributes from question
    query_attrs = extract_descriptor_attributes(query)
    
    query_attrs_formatted = format_descriptor_attributes(query_attrs)

    print(query_attrs_formatted)

    # 2. Get table metadata from each table - table descriptor and table description
    table_info = schema_metadata_service.generate_all_metadata(include_columns=False).values()

    # 3. Rank tables based on number of attributes shared between query and table
    results = rank_documents(query_attrs_formatted, table_info)

    candidate_tables = [result[0] for result in results]

    print(candidate_tables)

    # 4. Filter tables
    filtered_tables = llm_filter_tables(candidate_tables)

    # 5. Get table metadata from each candindate table - table descriptor, table description, and sample rows
    table_metadata = schema_metadata_service.generate_all_metadata(include_columns=True, table_filter=filtered_tables, include_sample_rows=True)

    response = llm_generate_sql(table_metadata)

    schema_metadata_service.close()

    return response

if __name__ == "__main__":
    # generate_table_embeddings()
    
    query = "“What are the draft type options available for boilers?”"

    result = pipeline(query)

    print(result)


