# AI Agent for Building Energy Standards Data

A natural-language agent that answers questions about the BESD database (for example
"What is the minimum EER for an air-cooled chiller under 150 tons in 90.1-2022?"). It finds
the relevant tables, inspects their columns, and runs read-only SQL against the database.

> This replaces the earlier LangChain `setup_besd_agent` / `agent_factory.py` agent, which
> has been removed.

## Components

| Part | Location | Role |
|---|---|---|
| MCP server | `mcps/` | Exposes the database tools (below) |
| Agent | `agent/` | LLM agent, built with [`automa-ai`](https://pypi.org/project/automa-ai/), that calls the MCP tools. Served over A2A on port 10000 |
| Launcher | `build.py` | Starts the MCP server (SSE, port 11000) and the A2A agent server |
| Chat UI | `ui.py` | Streamlit front end that talks to the agent on `localhost:10000` |
| Table allowlist | `config.py` | `TABLE_NAMES`, the tables the agent can see, and the ranking weights |
| Table descriptions | `core/data/generated_table_descriptions.json` | One description per allowlisted table, shown in search results |

### MCP tools

| Tool | Purpose |
|---|---|
| `get_candidate_tables` | Ranks tables for a question from structured fields (domain, system, standard family, year, ...). Usually the first call |
| `get_table_metadata` | Columns and sample rows for a table |
| `get_unique_values` | Distinct values of a column, to validate filters before writing SQL |
| `list_tables`, `list_tables_with_descriptions` | The allowlisted tables |
| `run_sql` | Runs a SELECT query against the database |

`get_candidate_tables` scores each table from its **name** (domain, standard family, year,
system, compliance path), not from its description. Tables that tie on score are listed in
`TABLE_NAMES` order.

## Setup

Requires Python 3.12 or 3.13.

```bash
uv sync --group agent
```

Create a `.env` file in the repository root (it is gitignored):

```
MODEL=<model id>
MODEL_BASE_URL=<base URL, if you use a gateway or proxy>
API_KEY=<API key>
```

## Run

Run these in two terminals, from the repository root:

```bash
uv run python -m building_energy_standards_data.applications.ai_agent.build
uv run streamlit run building_energy_standards_data/applications/ai_agent/ui.py
```

The first command starts the MCP server on `127.0.0.1:11000` and the agent on port 10000.
The second opens the chat UI.

The database (`openstudio_standards.db`) is built from the JSON files in
`database_files/` the first time the server starts, and cached in
`~/.cache/building_energy_standards_data/` (override with `BESD_DB_PATH`).

## Use the MCP server from another project

The MCP server is also installable on its own, without the agent. Install the package with
the `mcp` extra and run the `besd-mcp` command (stdio transport by default). This works
once the package is published; before that, use a locally built wheel (see below):

```bash
uvx --from "building-energy-standards-data[mcp]" besd-mcp
```

See [docs/MCP_Local_Testing.md](../../../docs/MCP_Local_Testing.md) for testing it from a
locally built wheel. Options: `--transport {stdio,sse,http,streamable-http}`, `--host`,
`--port`, `--db-path`, `--rebuild`.

## Evaluate the agent

`evaluation/run_agent_eval.py` (at the repository root) sends the questions in
`evaluation/data/sample_questions.json` to a running agent and grades the answers with an
LLM judge. It is not part of CI and needs the agent running and the `.env` above.

```bash
uv run python evaluation/run_agent_eval.py                  # all questions
uv run python evaluation/run_agent_eval.py --ids TABLE-001  # a subset
uv run python evaluation/run_agent_eval.py --no-judge       # collect answers only
```

Results are written to `evaluation/results/` (gitignored). The reference answers cite
ASHRAE table numbers rather than this database's table names, so the judge scores values
and facts only. Treat the grades as approximate and review failures by hand.

## Maintenance

- **Adding tables or code versions:** add the table name to `TABLE_NAMES` in `config.py`
  and an entry for it in `generated_table_descriptions.json`. Tables missing from
  `TABLE_NAMES` are invisible to the agent. The allowlist covers the code-version-dependent
  tables; the `level_1_*`, `level_2_*` and `support_*` lookup tables are not included.
- **After editing the JSON data:** run the server with `--rebuild` (or delete the cached
  database) so the database is rebuilt.
- **Tests:** `uv run pytest tests/ai_agent` covers the MCP tools and helpers. It does not
  call an LLM.
