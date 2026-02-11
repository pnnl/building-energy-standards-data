from fine_tuning.find_table.rules import RULES
from fine_tuning.find_table.types import TableDescriptor


class TableParser:
    """Parses table names into structured TableDescriptor objects."""

    def parse(self, table: str) -> TableDescriptor:
        tokens = table.split("_")
        context = {}

        for rule in RULES:
            field, value = rule.apply(tokens)
            context[field] = value

        return TableDescriptor(table=table, **context)
