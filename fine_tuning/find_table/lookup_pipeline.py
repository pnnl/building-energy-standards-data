import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
import re

from fine_tuning.client import LLMClient, generate

from fine_tuning.find_table.table_metadata import SchemaMetadataService
from fine_tuning.find_table.types import TableDescriptor
from fine_tuning.find_table.utils import (
    build_descriptor_prompt,
    dict_to_prompt_string,
    get_field_weights,
    run_sqlite_query,
)

TOP_K = 3

FIELD_WEIGHTS = get_field_weights(TableDescriptor)

TABLE_NAMES = [
    "hvac_minimum_requirements_motors_90_1",
    "hvac_minimum_requirements_motors_90_1_prm",
    "hvac_minimum_requirements_motors_IECC",
    "hvac_minimum_requirements_motors_189_1",
    "hvac_minimum_requirements_water_heaters_90_1",
    "hvac_minimum_requirements_water_heaters_90_1_prm",
    "hvac_minimum_requirements_water_heaters_IECC",
    "hvac_minimum_requirements_water_heaters_189_1",
    "hvac_minimum_requirements_heat_rejection_90_1",
    "hvac_minimum_requirements_heat_rejection_IECC",
    "hvac_minimum_requirements_heat_rejection_90_1_prm",
    "hvac_minimum_requirements_heat_rejection_189_1",
    "hvac_minimum_requirements_unitary_air_conditioners_90_1",
    "hvac_minimum_requirements_unitary_air_conditioners_90_1_prm",
    "hvac_minimum_requirements_unitary_air_conditioners_IECC",
    "hvac_minimum_requirements_unitary_air_conditioners_189_1",
    "hvac_minimum_requirements_heat_pumps_cooling_90_1",
    "hvac_minimum_requirements_heat_pumps_cooling_90_1_prm",
    "hvac_minimum_requirements_heat_pumps_cooling_IECC",
    "hvac_minimum_requirements_heat_pumps_cooling_189_1",
    "hvac_minimum_requirements_heat_pumps_heating_90_1",
    "hvac_minimum_requirements_heat_pumps_heating_90_1_prm",
    "hvac_minimum_requirements_heat_pumps_heating_IECC",
    "hvac_minimum_requirements_heat_pumps_heating_189_1",
    "hvac_minimum_requirements_chillers_90_1",
    "hvac_minimum_requirements_chillers_90_1_prm",
    "hvac_minimum_requirements_chillers_IECC",
    "hvac_minimum_requirements_chillers_189_1",
    "hvac_minimum_requirements_boilers_90_1",
    "hvac_minimum_requirements_boilers_90_1_prm",
    "hvac_minimum_requirements_boilers_IECC",
    "hvac_minimum_requirements_boilers_189_1",
    "hvac_minimum_requirements_furnaces_90_1",
    "hvac_minimum_requirements_furnaces_90_1_prm",
    "hvac_minimum_requirements_furnaces_IECC",
    "hvac_minimum_requirements_furnaces_189_1",
    "level_3_lighting_90_1_2022",
    "level_3_lighting_90_1_2019",
    "level_3_lighting_90_1_2016",
    "level_3_lighting_90_1_2013",
    "level_3_lighting_90_1_2010",
    "level_3_lighting_90_1_2007",
    "level_3_lighting_90_1_2004",
    "level_3_lighting_90_1_2022_prm",
    "level_3_lighting_90_1_2019_prm",
    "level_3_lighting_90_1_2016_prm",
    "level_3_lighting_90_1_2013_prm",
    "level_3_lighting_90_1_2010_prm",
    "level_3_lighting_90_1_2007_prm",
    "level_3_lighting_90_1_2004_prm",
    "level_3_lighting_IECC_2021",
    "level_3_lighting_IECC_2018",
    "level_3_lighting_IECC_2015",
    "level_3_lighting_IECC_2012",
    "level_3_lighting_IECC_2009",
    "level_3_lighting_IECC_2006",
    "level_3_ventilation_62_1_2022",
    "level_3_ventilation_62_1_2019",
    "level_3_ventilation_62_1_2016",
    "level_3_ventilation_62_1_2013",
    "level_3_ventilation_62_1_2010",
    "level_3_ventilation_62_1_2007",
    "level_3_ventilation_62_1_2004",
    "level_3_ventilation_62_1_1999",
    "system_requirements_energy_recovery_90_1",
    "system_requirements_energy_recovery_IECC",
    "system_requirements_energy_recovery_90_1_prm",
    "system_requirements_air_economizer_90_1",
    "system_requirements_air_economizer_90_1_prm",
    "system_requirements_air_economizer_IECC",
    "hvac_minimum_requirements_computer_room_air_conditioners_90_1",
    "hvac_minimum_requirements_computer_room_air_conditioners_IECC",
    "hvac_minimum_requirements_computer_room_air_conditioners_189_1",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_90_1",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_IECC",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_189_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_90_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_90_1_prm",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_189_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_IECC",
    "hvac_minimum_requirements_walkin_freezers_coolers_90_1",
    "hvac_minimum_requirements_walkin_freezers_coolers_90_1_prm",
    "hvac_minimum_requirements_walkin_freezers_coolers_189_1",
    "hvac_minimum_requirements_walkin_freezers_coolers_IECC",
    "exterior_lighting_90_1",
    "exterior_lighting_90_1_prm",
    "exterior_lighting_IECC",
    "envelope_thermal_bridging_requirements_IECC",
    "envelope_thermal_bridging_requirements_90_1",
    "system_requirements_fan_power_allowance_90_1",
    "envelope_requirements_90_1",
    "envelope_requirements_90_1_prm",
    "envelope_requirements_IECC",
]


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
        print(f"1.\nExtracted attributes:\n{query_attrs}\n\n")

        # 2. Get table metadata and rank by attribute matching
        table_metadata = self.schema_service.generate_all_metadata(
            table_filter=TABLE_NAMES, include_columns=False, include_descriptor=True
        )

        ranked_results = self.rank_tables(query_attrs, table_metadata)
        print(ranked_results)
        candidate_tables = [result[0] for result in ranked_results]
        print(f"2.\nCandidate tables: {candidate_tables}\n\n")

        # 3. Filter candidates with LLM
        filtered_tables = self.llm_filter_tables(query, candidate_tables)
        print(f"3.\nFiltered tables: {filtered_tables}\n\n")

        # 4. Generate SQL
        detailed_metadata = self.schema_service.generate_all_metadata(
            table_filter=filtered_tables,
            include_columns=True,
            include_sample_rows=True,
            include_descriptions=True,
            include_descriptor=False,
        )

        sql = self.llm_generate_sql(query, detailed_metadata)
        print(f"4.\nGenerated SQL:\n{sql}\n\n")

        with self.schema_service._connect() as conn:
            results = run_sqlite_query(sql, conn)

        if not results:
            results = "No results found or an error occurred during query execution."
        print(results)

        return self.llm_interpret_results(query, results)

    def extract_descriptor_attributes(self, query: str) -> Optional[Dict]:
        """Use LLM to extract structured attributes from user query."""
        prompt = self._build_extraction_prompt(query)
        response = self.llm.generate(prompt)
        return self.llm.extract_json_from_text(response)

    def _build_extraction_prompt(self, query: str) -> str:
        descriptor_prompt = build_descriptor_prompt(TableDescriptor)

        print(descriptor_prompt)

        return f"""Extract the descriptor attributes from the following user query about building energy standards data. We are using this data to find a specific table in a database.

User query:
\"\"\"{query}\"\"\"

Return a JSON object with the following fields:
{descriptor_prompt}

Do **not** include any other explanation, text, or formatting. Only output the JSON object."""

    def rank_tables(
        self, query_attrs: dict, all_table_metadata: dict, top_k: Optional[int] = None
    ):
        top_k = top_k or self.top_k
        ranked = []
        for table_name, table_metadata in all_table_metadata.items():

            score = 0.0
            for field, ref_value in query_attrs.items():
                if ref_value == None:
                    continue

                weight = FIELD_WEIGHTS.get(field, 1.0)

                doc_value = table_metadata["category"].get(field)

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

        print("Filter prompt:\n", prompt)
        response = self.llm.generate(prompt)

        return [t.strip() for t in response.split(",") if t.strip()]

    def llm_generate_sql(self, query: str, table_metadata: Dict[str, str]) -> str:
        """Generate SQL query using table metadata."""
        table_info = dict_to_prompt_string(table_metadata)

        prompt = f"""Use the following SQL tables:
{table_info}

Answer the user query by writing a single SQL query:
"{query}"

Do not include an explanation."""

        print(f"SQL generation prompt:\n{prompt}\n")
        return self.llm.generate(prompt)

    def llm_interpret_results(self, query: str, results) -> str:
        """Generate SQL query using table metadata."""
        prompt = f"""Use these results from the building energy standards database to answer the user query:
{results}

User query:
"{query}"
Provide a concise answer based on the results. If the results do not contain relevant information, say "Unable to answer the question." Do not include any other text."""

        return self.llm.generate(prompt)

    def close(self):
        self.schema_service.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def generate_table_descriptions(
    schema_service: Optional[SchemaMetadataService] = None,
    output_path: str = "data/generated_table_descriptions.json",
) -> Dict[str, str]:
    """Generate LLM descriptions for all tables (one-time operation)."""
    service = schema_service or SchemaMetadataService()
    generated = {}

    for table_name in service.get_table_names(TABLE_NAMES):
        descriptor = service.parse_table_name(table_name)
        columns = service.render_schema(service.get_schema(table_name))
        metadata = service.generate_all_metadata(
            descriptor, table_name=table_name, columns=columns
        )
        metadata_text = dict_to_prompt_string(metadata)

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