# AGENTS.md — Building Energy Standards Data (BESD)

## What This Project Is

BESD is a Python library + SQLite database holding prescriptive building energy code requirements from:
- **ASHRAE 90.1** (2004–2025, including Appendix G/PRM variants)
- **ASHRAE 62.1** (1999–2022, ventilation)
- **IECC** (2006–2024)
- **ASHRAE 189.1** (select versions)

Primary consumer: the **openstudio-standards** Ruby gem. Data covers lighting power densities, ventilation rates, HVAC equipment minimums, envelope requirements, schedules, and occupant types.

---

## Repository Layout

```
building_energy_standards_data/
  applications/
    database_maintenance.py     # Core API: create/export DB from JSON or CSV
    ai_agent/                   # LangChain-based AI agent (optional)
  database_engine/
    database.py                 # DBOperation base class — ORM-like SQLite wrapper
    database_util.py
    assertions.py
  database_tables/              # 169 Python table classes (one per data table)
    level_1_space_types.py      # Master space type list
    level_2_*.py                # Space type mapping tables
    level_3_lighting_*.py       # Raw lighting requirements per code version
    level_3_ventilation_*.py    # Raw ventilation requirements per code version
    envelope_requirements_*.py
    hvac_minimum_requirements_*.py
    system_requirements_*.py
    support_*.py                # Materials, curves, schedules, occupants
    __init__.py                 # Dynamic discovery of all table classes
  database_files/               # ~100 JSON source files (the actual data)
  query/
    fetch/                      # Read API (by ID, key-values, field names)
    update/                     # Write/update API
  __init__.py
  client.py                     # Quick usage examples
tests/
  test_database.py              # Main test suite (445 lines)
  test_template.py
docs/
  Structure.md                  # Architecture & design decisions
  DeveloperNotes.md             # Contribution guidelines
  QuickStartGuide.md
```

---

## Architecture: Three-Level Space Type Hierarchy

Data is organized in three levels:

| Level | Description | Example |
|-------|-------------|---------|
| **Level 1** | Master space type names | "Office" |
| **Level 2** | Mapping to sub-space types | "Office - Open Plan", "Office - Enclosed" |
| **Level 3** | Code-specific requirements | LPD = 0.61 W/ft² for 90.1-2019 |

This separation allows multiple code versions to reference the same space type names without duplication.

---

## Key Classes and Patterns

### `DBOperation` ([building_energy_standards_data/database_engine/database.py](building_energy_standards_data/database_engine/database.py))

Base class for every data table. Provides:
- `create_a_table(conn)` — creates the SQLite table
- `add_a_record(conn, record)` / `add_records(conn, records)`
- `export_table_to_json(conn, save_dir)` / `export_table_to_csv(conn, save_dir)`
- `validate_record_datatype(record)` — enforces column schema
- `_preprocess_record(record)` — override hook for custom transforms

### Table class naming convention

Each table class lives in `database_tables/` and follows the pattern:
```python
# e.g., level_3_lighting_90_1_2019.py
class LightDef9012019Table(LightDef9012019):
    ...
```
Where `LightDef9012019` defines columns/schema and the `Table` subclass adds any version-specific logic.

### Data files → DB pipeline

```
database_files/*.json
       ↓  create_openstudio_standards_database_from_json(conn)
   SQLite DB (openstudio_standards.db)
       ↓  export_openstudio_standards_database_to_json(conn, save_dir)
   database_files/*.json  (round-trip)
```

CSV is also supported as an alternative import/export format.

---

## Common Tasks

### Adding a new code version (e.g., 90.1-2028 lighting)

1. Add a JSON data file: `building_energy_standards_data/database_files/level_3_lighting_90_1_2028.json`
2. Create a table class in `building_energy_standards_data/database_tables/level_3_lighting_90_1_2028.py` following the pattern of an existing version (e.g., `level_3_lighting_90_1_2025.py`)
3. The `__init__.py` auto-discovers table classes — no manual registration needed
4. Update `level_2_lighting_space_types.json` if new space types are introduced
5. Run tests: `poetry run pytest -v`

### Querying data

```python
import sqlite3
from building_energy_standards_data.applications.database_maintenance import (
    create_openstudio_standards_database_from_json
)
from building_energy_standards_data.query.fetch.database_table import (
    fetch_record_by_id, fetch_records_by_keyvalues
)

conn = sqlite3.connect(":memory:")
create_openstudio_standards_database_from_json(conn)
records = fetch_records_by_keyvalues(conn, "level_3_lighting_90_1_2019", {"lighting_primary_space_type": "Office"})
```

---

## Tech Stack

| Tool | Version | Role |
|------|---------|------|
| Python | 3.10+ | Language |
| SQLite3 | stdlib | Database |
| pytest | ^7.4.3 | Testing |
| black | 22.12.0 | Code formatter (enforced by CI) |
| Poetry | — | Dependency management |

**Optional** (AI agent feature): langchain, langchain-anthropic, streamlit.

---

## Tests

```bash
poetry run pytest -v          # all tests
poetry run pytest tests/test_database.py -v   # main suite only
```

Tests verify:
- Weak foreign key validation (referential integrity checks)
- JSON → DB → JSON round-trip consistency
- CSV → DB → CSV round-trip consistency
- Template/version metadata fetching

Test artifacts are written to `tests/test_artifacts/`.

---

## Code Style

- **Black** (line length 88) is mandatory. CI fails if code isn't formatted.
- Run before committing: `black building_energy_standards_data/ tests/`
- No type annotations required, but existing code uses docstrings on public methods.

---

## CI/CD

GitHub Actions (`.github/workflows/openstudio_standards_database.yml`) runs on every PR:
1. Black formatting check
2. `poetry run pytest -v` on Ubuntu 22.04 / Python 3.10

A passing PR also triggers a downstream action in the **openstudio-standards** repo.

---

## Key Docs to Read

- [docs/Structure.md](docs/Structure.md) — database architecture, space type hierarchy, methodology
- [docs/DeveloperNotes.md](docs/DeveloperNotes.md) — contribution workflow, how to expand the DB
- [docs/QuickStartGuide.md](docs/QuickStartGuide.md) — quick examples for creation, export, and query
