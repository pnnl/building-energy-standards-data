# Taxonomy Design Guide

*For Building Energy Standards Table Retrieval*

## Purpose

We are building an taxonomy to classify database tables containing building energy standards data (e.g., ASHRAE 90.1, IECC).

The taxonomy is used to:

1. Interpret natural language queries.
2. Match those queries to the correct database table.
3. Improve table ranking before SQL generation.

---

# How the Taxonomy Is Used

Each table in the database is assigned a structured descriptor (a set of semantic attributes).

When a user asks a question:

1. An LLM extracts taxonomy attributes from the query.
2. We compare the query attributes to table descriptors.
3. We rank tables using weighted matching.
4. The best table is passed to SQL generation.

So the taxonomy must:

* Be predictable enough for an LLM to extract reliably.
* Be discriminative enough to distinguish tables.
* Avoid unnecessary overlap between dimensions.

---

### Taxonomy Types (`types.py`)

The file `types.py` defines the taxonomy used across the system.

It contains:

- All taxonomy dimensions (as `StrEnum` classes)
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

If you add, rename, or remove taxonomy dimensions, you shoud update `rules.py` to have the changes be reflected in the table parser.
