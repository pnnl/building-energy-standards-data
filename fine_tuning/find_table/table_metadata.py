from dataclasses import fields
from pathlib import Path
import sqlite3
import json
from typing import Dict, List, Any, Optional

from fine_tuning.find_table.rules import RULES
from fine_tuning.find_table.types import TableDescriptor

class SchemaMetadataService:
    """Loads schemas from SQLite and generates metadata text for embeddings."""

    def __init__(
        self,
        db_path: str = "openstudio_standards.db",
        descriptions_path: str = "fine_tuning/find_table/data/generated_table_descriptions.json",
    ):
        self.conn = sqlite3.connect(db_path)
        self.descriptions_path = Path(descriptions_path)
        self._table_descriptions: Optional[Dict[str, str]] = None
        self._table_names: Optional[List[str]] = None
        self._schemas: Optional[Dict[str, List[Dict[str, Any]]]] = None

    def get_table_names(self, table_filter: Optional[List[str]] = None) -> List[str]:
        if self._table_names is None:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self._table_names = [row[0] for row in cursor.fetchall() if row[0]]

        if table_filter:
            return [t for t in self._table_names if t in table_filter]
        return self._table_names

    def get_schema(self, table: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        return [
            {
                "column": col_name,
                "type": col_type,
                "not_null": bool(notnull),
                "default": default,
                "primary_key": bool(pk),
            }
            for _, col_name, col_type, notnull, default, pk in columns
        ]

    def get_all_schemas(
        self, table_filter: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        if self._schemas is None:
            tables = self.get_table_names()
            self._schemas = {t: self.get_schema(t) for t in tables}

        if table_filter:
            return {t: self._schemas[t] for t in table_filter if t in self._schemas}
        return self._schemas
    
    def parse_table_name(self, table_name: str) -> TableDescriptor:
        tokens = table_name.split("_")
        context = {}

        for rule in RULES:
            field, value = rule.apply(tokens)
            context[field] = value

        return TableDescriptor(**context)

    @property
    def table_descriptions(self) -> Dict[str, str]:
        """Lazy-load table descriptions from JSON file."""
        if self._table_descriptions is None:
            self._table_descriptions = json.loads(self.descriptions_path.read_text())
        return self._table_descriptions

    @staticmethod
    def render_schema(columns: List[Dict[str, Any]]) -> List[str]:
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

    def generate_single_table_metadata(
        self,
        descriptor: Optional[TableDescriptor] = None,
        table_name: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ) -> str:
        """
        Render descriptor as labeled text.

        - Automatically reflects dataclass fields.
        - Optional control over null inclusion.
        - Optional custom label mapping.
        """

        table_metadata = {}

        if table_name:
            table_metadata["table_name"] = table_name

        if descriptor:
            if not isinstance(descriptor, TableDescriptor):
                raise TypeError("descriptor must be a TableDescriptor instance")

            descriptor_dict = {}
            for field in fields(descriptor):
                name = field.name
                value: Any = getattr(descriptor, name)
                label = name
                descriptor_dict[label] = value

            table_metadata["category"] = descriptor_dict

        if columns:
            table_metadata["columns"] = ", ".join(columns)

        return table_metadata

    def generate_all_metadata(
        self,
        table_filter: Optional[List[str]] = None,
        include_columns: bool = True,
        include_sample_rows: bool = False,
        include_descriptions: bool = False,
        include_descriptor: bool = False
    ) -> Dict[str, str]:
        """Generate metadata text for all tables (or filtered subset)."""
        schemas = self.get_all_schemas(table_filter)

        metadata = {}
        for table, schema in schemas.items():
            
            columns = self.render_schema(schema) if include_columns else None
            descriptor = self.parse_table_name(table) if include_descriptor else None

            metadata[table] = self.generate_single_table_metadata(
                descriptor, table, columns
            )

            if include_descriptions:
                metadata[
                    table
                ]["description"] = {self.table_descriptions.get(table, 'No description available.')}

            if include_sample_rows:
                from fine_tuning.data_processing.add_context import get_sample_rows

                sample_rows = get_sample_rows(conn=self.conn, table_name=table)
                metadata[table]["sample_rows"] = sample_rows

        return metadata

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()