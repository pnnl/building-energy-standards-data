from fine_tuning.find_table.types import *
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type
import requests
import json
from pathlib import Path
import re
from langchain_core.documents import Document

from langchain_community.vectorstores import Chroma

TOP_K = 3

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

db = Chroma(
    collection_name="osstd_table_name_rag",
    persist_directory="fine_tuning/find_table/db",
    embedding_function=embedding,
)

table_retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": TOP_K},
)

def cosine_similarity(a, b):
    return np.dot(a, b)  # embeddings normalized so dot product = cosine similarity


def add_if_not_exists(table_texts_dict):
    for table, text in table_texts_dict.items():
        results = db.get(
            limit=1,
            where={"table": table},
        )
        if results.get("ids") and results['ids'][0]:  # means a doc exists for this table
            # print(f"Skipping {table}, already embedded.")
            continue
        
        # If not found, add new doc
        doc = Document(page_content=text, metadata={"table": table})
        db.add_documents([doc])
        print(f"Added {table} to DB.")

@dataclass
class TableDescriptor:
    table: str

    domain: Domain
    topic: Optional[Topic]
    data_role: DataRole
    classification_type: Optional[ClassificationType]

    system: Optional[System]
    sub_system: Optional[SubSystem]

    standard_family: Optional[StandardFamily]
    standard_year: Optional[int]
    compliance_path: Optional[CompliancePath]


DOMAIN_PREFIXES = {
    "envelope": "envelope",
    "hvac": "hvac",
    "exterior": "exterior_lighting",
    "system": "system",
    "level": "space_classification",
    "support": "support",
}

SYSTEMS = {
    "variable_refrigerant_flow_systems": "vrf",
    "unitary_air_conditioners": "unitary_ac",
    "computer_room_air_conditioners": "crac",
    "water_heaters": "water_heater",
    "heat_rejection": "heat_rejection",
    "air_economizer": "air_economizer",
    "energy_recovery": "energy_recovery",
    "boilers": "boiler",
    "chillers": "chiller",
    "furnaces": "furnace",
    "motors": "motor",
}


def parse_table_name(table: str) -> TableDescriptor:
    tokens = table.split("_")

    compliance_path = CompliancePath.APPENDIX_G if tokens[-1] == "prm" else CompliancePath.PRESCRIPTIVE

    domain = next(
        (Domain(DOMAIN_PREFIXES[k]) for k in DOMAIN_PREFIXES.keys() if tokens[0] == k),
        Domain.UNKNOWN,
    )

    topic = None
    if "minimum" in tokens and "requirements" in tokens:
        topic = Topic.MINIMUM_REQUIREMENTS
    elif "requirements" in tokens:
        topic = Topic.REQUIREMENTS
    elif "lighting" in tokens:
        topic = Topic.LIGHTING_DATA
    elif "ventilation" in tokens:
        topic = Topic.VENTILATION_DATA
    elif "space" in tokens and "types" in tokens:
        topic = Topic.SPACE_TYPES

    # System lookup
    system = None
    for i in range(len(tokens)):
        for j in range(len(tokens), i, -1):
            candidate = "_".join(tokens[i:j])
            if candidate in SYSTEMS:
                system = System(SYSTEMS[candidate])
                break
        if system:
            break
        
    sub_system = None
    if "cooling" in tokens:
        sub_system = SubSystem.COOLING
    elif "heating" in tokens:
        sub_system = SubSystem.HEATING

    # Standard family + year
    standard_family = None
    standard_year = None

    if "IECC" in tokens:
        standard_family = StandardFamily.IECC
    elif "90" in tokens and "1" in tokens:
        standard_family = StandardFamily.ASHRAE_90_1
    elif "62" in tokens and "1" in tokens:
        standard_family = StandardFamily.ASHRAE_62_1
    elif "189" in tokens and "1" in tokens:
        standard_family = StandardFamily.ASHRAE_189_1

    for t in tokens:
        if t.isdigit() and len(t) == 4:
            standard_year = int(t)

    # Data role base default
    if domain == Domain.SUPPORT:
        data_role = DataRole.REFERENCE_DATA
    elif domain == Domain.SPACE_CLASSIFICATION:
        data_role = DataRole.CLASSIFICATION
    elif domain == Domain.UNKNOWN:
        data_role = DataRole.UNKNOWN
    else:
        data_role = DataRole.REQUIREMENTS

    # Schema-driven refinement for support domain
    if domain == Domain.SUPPORT:
        if table == "support_lighting_technologies":
            topic = Topic.LIGHTING_TECHNOLOGIES
            system = System.LIGHTING
        elif table == "support_occupant_physical_characteristics":
            topic = Topic.OCCUPANT_PHYSICAL_CHARACTERISTICS
        elif table == "support_occupant_energy_behavior":
            topic = Topic.OCCUPANT_ENERGY_BEHAVIOR
            data_role = DataRole.NORMATIVE_INPUTS
        elif table == "support_standard_templates":
            topic = Topic.STANDARD_TEMPLATES
        elif table == "support_performance_curves":
            topic = Topic.PERFORMANCE_CURVES
        elif "schedule" in table:
            topic = Topic.SCHEDULES
            data_role = DataRole.NORMATIVE_INPUTS

    classification_type = None
    if domain == Domain.SPACE_CLASSIFICATION:
        if topic == Topic.SPACE_TYPES:
            classification_type = ClassificationType.TAXONOMY
        elif "subtypes" in tokens or "subspace" in tokens:
            classification_type = ClassificationType.SUBCLASSIFICATION

    return TableDescriptor(
        table=table,
        domain=domain,
        topic=topic,
        data_role=data_role,
        classification_type=classification_type,
        system=system,
        sub_system=sub_system,
        standard_family=standard_family,
        standard_year=standard_year,
        compliance_path=compliance_path,
    )

def load_schema_docs(sqlite_path: Optional[str] = "openstudio_standards.db"):
    import sqlite3


    # --- Extract SQL schema from SQLite ---
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schemas: Dict[str, List[Dict[str, Any]]] = {}

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()

        schemas[table] = [
            {
                "column": col_name,
                "type": col_type,
                "not_null": bool(notnull),
                "default": default,
                "primary_key": bool(pk),
            }
            for _, col_name, col_type, notnull, default, pk in columns
        ]

    conn.close()
    return schemas

def render_schema_doc(table: str, columns: List[Dict[str, Any]]) -> str:
    lines = []
    for c in columns:
        line = f"- {c['column']} ({c['type']})"
        if c.get("primary_key"):
            line += " [PK]"
        if c.get("not_null"):
            line += " NOT NULL"
        if c.get("default") is not None:
            line += f" DEFAULT {c['default']}"
        lines.append(line)
    return lines

def generate_table_metadata_text(table_descriptor: TableDescriptor, table_name=None, columns=None) -> str:
    """
    Create a text summary of the table metadata for embedding or indexing.

    :param table_descriptor: TableDescriptor object
    :param table_description: Optional string description of the table
    :param columns: Optional list of column names
    :return: A string summarizing the table metadata
    """

    parts = []
    if table_name:
        parts.append(f"Table Name: {table_name}")
    parts.append(f"Domain: {table_descriptor.domain}")
    if table_descriptor.topic:
        parts.append(f"Topic: {table_descriptor.topic}")
    if table_descriptor.data_role:
        parts.append(f"Data role: {table_descriptor.data_role}")
    if table_descriptor.classification_type:
        parts.append(f"Classification type: {table_descriptor.classification_type}")
    if table_descriptor.system:
        parts.append(f"System: {table_descriptor.system}")
    if table_descriptor.sub_system:
        parts.append(f"Sub-system: {table_descriptor.sub_system}")
    if table_descriptor.standard_family:
        parts.append(f"Standard family: {table_descriptor.standard_family}")
    if table_descriptor.standard_year:
        parts.append(f"Standard year: {table_descriptor.standard_year}")
    if table_descriptor.compliance_path:
        parts.append(f"Compliance path: {table_descriptor.compliance_path}")

    if columns:
        cols_str = ", ".join(columns)
        parts.append(f"Columns: {cols_str}")

    return "\n".join(parts)


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

def generate_descriptions():
    schemas = load_schema_docs()
    tables = list(schemas.keys())

    generated_descriptions = {}

    for table in tables:
        table_descriptor = parse_table_name(table)
        columns = render_schema_doc(table, schemas[table])
        metadata_text = generate_table_metadata_text(table_descriptor, table_name=table, columns=columns)

        prompt = (
            f"Write a clear, 100-150 token, concise description for the database table named '{table}'. "
            "This database contains tabulated building energy standards data used in energy simulation and compliance evaluation. It includes key prescriptive requirements such as equipment efficiency and thermal performance assumptions, but does not cover all exceptions or nuanced code conditions. Use this context to write a clear, concise description for the following table."
            "Include the domain, system, and relevant standard or compliance path it supports. "
            "Describe the key data it holds, such as important columns and their role, including any date ranges, efficiency metrics, capacity limits, or annotations. "
            "Explain how this table is typically used to support compliance or reference within its context.\n\n"
            f"Here is the metadata:\n{metadata_text}"
        )

        generated_description = generate(prompt)
        generated_descriptions[table] = generated_description

        # print(f"Generated description for {table}:\n{generated_description}")
        # print("-" * 40)

    with open("generated_table_descriptions.json", "w") as f:
        json.dump(generated_descriptions, f, indent=2)

def query_db(query) -> list[Document]:
    table_docs = table_retriever.get_relevant_documents(query)
    return table_docs

def get_table_descriptions():
    json_path = "fine_tuning/find_table/generated_table_descriptions.json"
    data = json.loads(Path(json_path).read_text())
    return data


def generate_table_embeddings():
    table_metadata_texts = generate_table_metadata()

    add_if_not_exists(table_metadata_texts)

def generate_table_metadata(include_columns=True):
    schemas = load_schema_docs()
    tables = list(schemas.keys())

    table_descriptors = {t: parse_table_name(t) for t in tables}

    table_metadata_texts = {
        t: generate_table_metadata_text(table_descriptors[t], t, render_schema_doc(t, schemas[t]) if include_columns else None)
        for t in tables
    }

    return table_metadata_texts

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
            if score == max_score:
                print(
                    doc_fields["Table Name"],
                    [(ref_fields[f], doc_fields[f]) for f in shared_fields]
                )
        ranked.append((doc_fields["Table Name"], score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    max_ranking = ranked[0][1]
    ranked = [ranking for ranking in ranked if ranking[1] == max_ranking]

    return ranked

def pipeline(query: str):
    """
    Idea: We can categorize the tables into having different attributes,
    and then find the closest matching table to a query by assigning the
    query the same attributes.
    """

    # 1. Using LLM, extract 'descriptor' attributes from question
    query_attrs = extract_descriptor_attributes(query)
    
    query_attrs_formatted = format_descriptor_attributes(query_attrs)

    # 2. Get table metadata from each table - table descriptor and table description
    table_info = generate_table_metadata(include_columns=False).values()

    # 3. Rank tables based on number of attributes shared between query and table
    results = rank_documents(query_attrs_formatted, table_info)

    candidate_tables = [result[0] for result in results]

    # return candidate_tables
    table_descriptions = get_table_descriptions()

    candidate_tables_prompt = "\n\n".join(
        [f"Table: {t}\nDescription: {table_descriptions[t]}" for t in candidate_tables]
    )

    print(candidate_tables_prompt)
    
    prompt = f"""
    Given the user query:
    "{query}"

    And the following candidate table descriptions:

    {candidate_tables_prompt}

    Please reply with only the database table name(s) necessary to answer the query.
    If multiple, separate them by commas. Do not add any other text.
    """
    
    # Step 5: Ask LLM for final table selection
    response = generate(prompt)
    
    table_names = [t.strip() for t in response.split(",") if t.strip()]

    return table_names


if __name__ == "__main__":
    # generate_table_embeddings()
    
    query = "What is the maximum permitted assembly U-value for a residential exterior mass wall in Climate Zone 3A according to IECC-2012?"

    result = pipeline(query)

    print(result)
    # attributes = extract_descriptor_attributes(query)
    # print(attributes)


