import json
from pathlib import Path
from typing import Dict, List, Optional

from fine_tuning.client import LLMClient, generate

from fine_tuning.find_table.table_metadata import SchemaMetadataService
from fine_tuning.find_table.types import (
    Domain, Topic, DataRole, ClassificationType,
    System, SubSystem, StandardFamily, CompliancePath,
)

TOP_K = 3

DESCRIPTOR_KEY_MAP = {
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


FIELD_WEIGHTS = {
    "System": 5.0,        # High weight - most discriminating
    "Sub-system": 3.0,
    "Domain": 1.0,
    "Topic": 1.5,
    "Standard family": 1.0,
    "Standard year": 2.0,
    "Compliance path": 1.0,
    "Data role": 0.5,
    "Classification type": 1.0,
}

class QueryPipeline:
    """Orchestrates query → table selection → SQL generation pipeline."""

    def __init__(
        self,
        schema_service: Optional[SchemaMetadataService] = None,
        llm_client: Optional[LLMClient] = None,
        top_k: int = TOP_K,
    ):
        self.schema_service = schema_service or SchemaMetadataService()
        self.llm = llm_client or LLMClient()
        self.top_k = top_k

    def run(self, query: str) -> str:
        """
        Execute the full pipeline:
        1. Extract descriptor attributes from query
        2. Rank tables by attribute matching
        3. Filter candidates with LLM
        4. Generate SQL
        """
        # 1. Extract descriptor attributes from query
        query_attrs = self.extract_descriptor_attributes(query)
        query_attrs_formatted = self.format_descriptor_attributes(query_attrs)
        print(f"Extracted attributes:\n{query_attrs_formatted}\n")

        # 2. Get table metadata and rank by attribute matching
        table_metadata = self.schema_service.generate_all_metadata(include_columns=False)
        ranked_results = self.rank_tables(query_attrs_formatted, list(table_metadata.values()))
        candidate_tables = [result[0] for result in ranked_results]
        print(f"Candidate tables: {candidate_tables}\n")

        # 3. Filter candidates with LLM
        filtered_tables = self.llm_filter_tables(query, candidate_tables)
        print(f"Filtered tables: {filtered_tables}\n")

        # 4. Generate SQL
        detailed_metadata = self.schema_service.generate_all_metadata(
            include_columns=True,
            table_filter=filtered_tables,
            include_sample_rows=True,
            include_descriptions=True
        )
        print(f"The detailed metadata: {detailed_metadata}")

        sql = self.llm_generate_sql(query, detailed_metadata)

        return sql

    def extract_descriptor_attributes(self, query: str) -> Optional[Dict]:
        """Use LLM to extract structured attributes from user query."""
        prompt = self._build_extraction_prompt(query)
        response = self.llm.generate(prompt)
        return self.llm.extract_json_from_text(response)

    def _build_extraction_prompt(self, query: str) -> str:
        return f"""Extract the descriptor attributes from the following user query about building energy standards data. We are using this data to find a specific table in a database.

User query:
\"\"\"{query}\"\"\"

Return a JSON object with the following fields:
- domain (string or null): One of {self.llm.enum_values(Domain) + [None]}. Represents the high-level area such as HVAC, envelope, support, etc.
- topic (string or null): One of {self.llm.enum_values(Topic) + [None]}. Describes the subject focus like minimum requirements, lighting data, or space types.
- data_role (string or null): One of {self.llm.enum_values(DataRole) + [None]}. Indicates the role of the data, e.g., requirements, reference_data, or normative_inputs.
- classification_type (string or null): One of {self.llm.enum_values(ClassificationType) + [None]}. Specifies the classification nature, like taxonomy or subclassification.
- system (string or null): One of {self.llm.enum_values(System) + [None]}. The specific system involved, such as motor, water_heater, lighting, etc.
- sub_system (string or null): One of {self.llm.enum_values(SubSystem) + [None]}. Further subdivision such as heating or cooling subsystems. This only applies to heat pumps.
- standard_family (string or null): One of {self.llm.enum_values(StandardFamily) + [None]}. The code or standard family. If necessary to answer query but not specified in the query, default to ASHRAE_90_1.
- standard_year (integer four-digit year or null): The year of the applicable standard.
- compliance_path (string or null): One of {self.llm.enum_values(CompliancePath) + [None]}. The compliance method, such as "prescriptive" (default) or "appendix_g" which corresponds to tables with the "prm" suffix.

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

Do **not** include any other explanation, text, or formatting. Only output the JSON object."""

    @staticmethod
    def format_descriptor_attributes(attrs: Dict) -> str:
        """Format descriptor attributes as labeled text."""
        if not attrs:
            return ""

        lines = []
        if attrs.get("table"):
            lines.append(f"Table: {attrs['table']}")

        for key, label in DESCRIPTOR_KEY_MAP.items():
            val = attrs.get(key)
            lines.append(f"{label}: {val if val is not None else 'null'}")

        return "\n".join(lines)

    @staticmethod
    def parse_document(doc: str) -> Dict[str, str]:
        """Parse a document string into {field: value}, ignoring null values."""
        field_values = {}
        for line in doc.strip().splitlines():
            if ":" not in line:
                continue
            field, value = line.split(":", 1)
            field = field.strip()
            value = value.strip()
            if value.lower() != "null":
                field_values[field] = value
        return field_values

    def rank_tables(self, reference_doc: str, doc_list: List[str], top_k: Optional[int] = None):
        top_k = top_k or self.top_k
        ref_fields = self.parse_document(reference_doc)

        ranked = []
        for doc in doc_list:
            doc_fields = self.parse_document(doc)
            table_name = doc_fields.get("Table Name", "")

            score = 0.0
            for field, ref_value in ref_fields.items():
                if ref_value == "null":
                    continue
                    
                weight = FIELD_WEIGHTS.get(field, 1.0)
                doc_value = doc_fields.get(field)

                if doc_value == ref_value:
                    score += weight
                elif doc_value is None:
                    score -= weight * 0.25
                else:
                    score -= weight * 1.0

            ranked.append((table_name, score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def llm_filter_tables(self, query: str, candidate_tables: List[str]) -> List[str]:
        """Use LLM to select the most relevant tables from candidates."""
        descriptions = self.schema_service.table_descriptions

        candidate_prompt = "\n\n".join(
            f"Table: {t}\nDescription: {descriptions.get(t, 'No description available')}"
            for t in candidate_tables
        )

        prompt = f"""Given the user query: "{query}"

And the following candidate table descriptions:
{candidate_prompt}

Please reply with ONLY the database table name(s) that may help to answer the query.
If multiple, separate them by commas. Do not add any other text and do not explain your decision."""

        response = self.llm.generate(prompt)

        return [t.strip() for t in response.split(",") if t.strip()]

    def llm_generate_sql(self, query: str, table_metadata: Dict[str, str]) -> str:
        """Generate SQL query using table metadata."""
        table_info = "\n\n".join(table_metadata.values())

        prompt = f"""Use the following SQL tables:
{table_info}

Answer the user query by writing a single SQL query:
"{query}"

Do not include an explanation."""

        print(f"SQL generation prompt:\n{prompt}\n")
        return self.llm.generate(prompt)


    def close(self):
        self.schema_service.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def generate_table_descriptions(
    schema_service: Optional[SchemaMetadataService] = None,
    output_path: str = "generated_table_descriptions.json",
) -> Dict[str, str]:
    """Generate LLM descriptions for all tables (one-time operation)."""
    service = schema_service or SchemaMetadataService()
    generated = {}

    for table_name in service.get_table_names():
        descriptor = service.get_table_descriptor(table_name)
        columns = service.render_schema(service.get_schema(table_name))
        metadata_text = service.generate_metadata_text(
            descriptor, table_name=table_name, columns=columns
        )

        prompt = f"""Write a clear, 100-150 token, concise description for the database table named '{table_name}'.

This database contains tabulated building energy standards data used in energy simulation and compliance evaluation. It includes key prescriptive requirements such as equipment efficiency and thermal performance assumptions, but does not cover all exceptions or nuanced code conditions.

Include the domain, system, and relevant standard or compliance path it supports.
Describe the key data it holds, such as important columns and their role, including any date ranges, efficiency metrics, capacity limits, or annotations.
Explain how this table is typically used to support compliance or reference within its context.

Here is the metadata:
{metadata_text}"""

        generated[table_name] = generate(prompt)

    with open(output_path, "w") as f:
        json.dump(generated, f, indent=2)

    if schema_service is None:
        service.close()

    return generated