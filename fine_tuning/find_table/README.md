# Ontology Design Guide

*For Building Energy Standards Table Retrieval*

## Purpose

We are building an ontology to classify database tables containing building energy standards data (e.g., ASHRAE 90.1, IECC).

The ontology is used to:

1. Interpret natural language queries.
2. Match those queries to the correct database table.
3. Improve table ranking before SQL generation.

---

# How the Ontology Is Used

Each table in the database is assigned a structured descriptor (a set of semantic attributes).

When a user asks a question:

1. An LLM extracts ontology attributes from the query.
2. We compare the query attributes to table descriptors.
3. We rank tables using weighted matching.
4. The best table is passed to SQL generation.

So the ontology must:

* Be predictable enough for an LLM to extract reliably.
* Be discriminative enough to distinguish tables.
* Avoid unnecessary overlap between dimensions.

---

### Ontology Types (`types.py`)

The file `types.py` defines the ontology used across the system.

It contains:

- All ontology dimensions (as `StrEnum` classes)
- The `TableDescriptor` dataclass
- Field-level ranking weights

This file represents a contract between:

- Table name parsing
- LLM query extraction
- Table ranking logic

---

#### `rules.py`

Contains the parsing rules.

This is the **source of truth** for how table names are interpreted.

#### `parsing_rules` and `RULES`

- `RULES` is an **ordered list** of rule objects applied to table-name tokens.
- Rule order matters when multiple rules could match the same token.

If you add, rename, or remove ontology dimensions, you shoud update `rules.py` to have the changes be reflected in the table parser.

#### Example: `parse_table.py`

```python
from utils import parse_table_name

def main():
    table_name = "level_3_lighting_90_1_2010_prm"
    descriptor = parse_table_name(table_name)

    print("Table:", descriptor.table)
    print("Parsed Descriptor:")
    print(descriptor)

if __name__ == "__main__":
    main()