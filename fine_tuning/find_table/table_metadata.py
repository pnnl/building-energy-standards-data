from dataclasses import dataclass, fields
from pathlib import Path
import sqlite3
import json
from typing import Dict, List, Any, Optional

from fine_tuning.data_processing.add_context import get_sample_rows

from .table_parser import TableParser, TableDescriptor


class SchemaMetadataService:
    """Loads schemas from SQLite and generates metadata text for embeddings."""

    def __init__(
        self,
        db_path: str = "openstudio_standards.db",
        descriptions_path: str = "fine_tuning/find_table/generated_table_descriptions.json",
    ):
        self.conn = sqlite3.connect(db_path)
        self.parser = TableParser()
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

    def generate_metadata_text(
        self,
        descriptor: TableDescriptor,
        table_name: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ) -> str:
        """
        Render descriptor as labeled text.

        - Automatically reflects dataclass fields.
        - Optional control over null inclusion.
        - Optional custom label mapping.
        """

        if not isinstance(descriptor, TableDescriptor):
            raise TypeError("descriptor must be a TableDescriptor instance")

        parts = []

        if table_name:
            parts.append(f"Table Name: {table_name}")

        for field in fields(descriptor):
            name = field.name
            value: Any = getattr(descriptor, name)

            if name == "table":
                continue  # skip internal field

            label = name
            parts.append(f"{label}: {value}")

        if columns:
            parts.append("Columns:")
            parts.append(", ".join(columns))

        return "\n".join(parts)

    def generate_all_metadata(
        self,
        include_columns: bool = True,
        table_filter: Optional[List[str]] = None,
        include_sample_rows: bool = False,
        include_descriptions: bool = False,
    ) -> Dict[str, str]:
        """Generate metadata text for all tables (or filtered subset)."""
        schemas = self.get_all_schemas(table_filter)

        metadata_texts = {}
        for table, schema in schemas.items():
            descriptor = self.parser.parse(table)
            columns = self.render_schema(schema) if include_columns else None
            metadata_texts[table] = self.generate_metadata_text(
                descriptor, table, columns
            )

            if include_descriptions:
                metadata_texts[
                    table
                ] += f"\nDescription:\n{self.table_descriptions.get(table, 'No description available.')}"

            if include_sample_rows:
                sample_rows = get_sample_rows(conn=self.conn, table_name=table)
                metadata_texts[table] += f"\nSample Rows:\n{sample_rows}"

        return metadata_texts

    def get_table_descriptor(self, table: str) -> TableDescriptor:
        """Convenience method to parse a single table name."""
        return self.parser.parse(table)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
