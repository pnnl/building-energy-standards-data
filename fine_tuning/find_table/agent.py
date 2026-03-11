"""
agent.py — LangChain tool-calling agent for building energy standards DB.
"""

import json
import dotenv
import re
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ── Your existing imports ──────────────────────────────────────────────
from fine_tuning.client import LLMClient, generate
from fine_tuning.find_table.lookup_pipeline import TABLE_NAMES

from fine_tuning.find_table.table_metadata import SchemaMetadataService
from fine_tuning.find_table.types import TableDescriptor, Domain, Topic, System, SubSystem, StandardFamily, CompliancePath
from fine_tuning.find_table.utils import (
    build_descriptor_prompt,
    dict_to_prompt_string,
    get_field_weights,
    run_sqlite_query,
)


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _enum_values_display(enum_cls) -> str:
    """'val_a', 'val_b', 'val_c'"""
    return ", ".join(f"'{e.value}'" for e in enum_cls)


def _resolve_enum(enum_cls, value: Any):
    """Case-insensitive, underscore/hyphen-tolerant enum lookup.

    Returns the enum member or None (so scoring gracefully skips it).
    """
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    normalised = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    for member in enum_cls:
        if member.value.lower() == normalised or member.name.lower() == normalised:
            return member
    return None


# ═══════════════════════════════════════════════════════════════════════
#  PYDANTIC INPUT SCHEMA — get_candidate_tables
# ═══════════════════════════════════════════════════════════════════════

class CandidateTableSearch(BaseModel):
    """Structured descriptor for searching the table catalogue."""

    domain: str = Field(
        description=(
            "The broad building-system domain this data belongs to. "
            "REQUIRED — always set this. "
            f"Valid values: [{_enum_values_display(Domain)}]."
        ),
    )
    topic: Optional[str] = Field(
        default=None,
        description=(
            "The category of data or requirement type. "
            f"Valid values: [{_enum_values_display(Topic)}]. "
            "Set null if uncertain. (weight 1.5)"
        ),
    )
    system: Optional[str] = Field(
        default=None,
        description=(
            "The specific equipment or system type. "
            "THIS IS THE STRONGEST SIGNAL (weight 5.0) — set it whenever "
            "the user mentions a piece of equipment (chiller, boiler, "
            "motor, fan, heat pump, etc.). "
            f"Valid values: [{_enum_values_display(System)}]. "
            "Set null if uncertain."
        ),
    )
    sub_system: Optional[str] = Field(
        default=None,
        description=(
            "A sub-system qualifier that distinguishes the operating "
            "mode or side of a system, e.g. heating vs cooling. "
            f"Valid values: [{_enum_values_display(SubSystem)}]. "
            "Set null if uncertain. (weight 3.0)"
        ),
    )
    standard_family: Optional[str] = Field(
        default=None,
        description=(
            "The code or standard family the data was published under. "
            f"Valid values: [{_enum_values_display(StandardFamily)}]. "
            "Set null if uncertain. (weight 1.0)"
        ),
    )
    standard_year: Optional[int] = Field(
        default=None,
        description=(
            "The edition year of the standard, e.g. 2019, 2022. "
            "Set null if not mentioned. (weight 2.0)"
        ),
    )
    compliance_path: Optional[str] = Field(
        default=None,
        description=(
            "The compliance methodology or path. "
            f"Valid values: [{_enum_values_display(CompliancePath)}]. "
            "Defaults to prescriptive when not specified. (weight 1.0)"
        ),
    )


# ═══════════════════════════════════════════════════════════════════════
#  TOOL FACTORY
# ═══════════════════════════════════════════════════════════════════════

def create_tools(
    schema_service: "SchemaMetadataService",
    top_k: int = 3,
) -> List:
    """Create the four agent tools, all closing over a shared schema service."""

    svc = schema_service

    # ── 1. list_tables ──────────────────────────────────────────────

    @tool
    def list_tables() -> str:
        """List every table in the building energy standards database.

        Returns each table name with a short description.  Use this to
        get a broad overview of what data is available *before* narrowing
        your search with `get_candidate_tables`.
        """
        tables = svc.get_table_names(TABLE_NAMES)
        descriptions = getattr(svc, "table_descriptions", {}) or {}
        lines = []
        for t in sorted(tables):
            desc = descriptions.get(t, "")
            short = (desc[:200] + " …") if len(desc) > 200 else desc
            lines.append(f"• {t}  —  {short}")
        return f"{len(tables)} tables available:\n\n" + "\n".join(lines)

    # ── 2. get_candidate_tables ─────────────────────────────────────

    @tool(args_schema=CandidateTableSearch)
    def get_candidate_tables(
        domain: str,
        topic: Optional[str] = None,
        system: Optional[str] = None,
        sub_system: Optional[str] = None,
        standard_family: Optional[str] = None,
        standard_year: Optional[int] = None,
        compliance_path: Optional[str] = None,
    ) -> str:
        """Find the most relevant tables by matching structured descriptor
        attributes against every table in the catalogue.

        ── WHEN TO CALL ──
        This should be your FIRST tool call for most questions.  Translate
        the user's intent into descriptor fields, and this tool will return
        a ranked shortlist.

        ── HOW SCORING WORKS ──
        Each field has a weight.  An exact match adds +weight, a mismatch
        subtracts -weight, and a null query field is ignored (no penalty).
        Field weights (highest → lowest):

            system        5.0   ← strongest signal
            sub_system    3.0
            standard_year 2.0
            topic         1.5
            domain        1.0
            standard_family 1.0
            compliance_path 1.0

        ── STRATEGY ──
        • Always set `domain`.
        • Set `system` whenever the user mentions equipment — it
          dominates the ranking.
        • Leave a field null when uncertain — a null is neutral, but a
          wrong value is heavily penalised.

        ── NEXT STEP ──
        Call `get_table_metadata` on the top result(s) to inspect columns
        and sample rows before writing SQL.
        """
        # Resolve strings → enum members (None on mismatch)
        query_attrs = {
            "domain":          _resolve_enum(Domain, domain),
            "topic":           _resolve_enum(Topic, topic),
            "system":          _resolve_enum(System, system),
            "sub_system":      _resolve_enum(SubSystem, sub_system),
            "standard_family": _resolve_enum(StandardFamily, standard_family),
            "standard_year":   standard_year,
            "compliance_path": _resolve_enum(CompliancePath, compliance_path),
        }

        # Fetch every table's descriptor
        table_metadata = svc.generate_all_metadata(
            table_filter=TABLE_NAMES,
            include_columns=False,
            include_descriptor=True,
        )

        # Score & rank
        ranked: List[tuple] = []
        FIELD_WEIGHTS = get_field_weights(TableDescriptor)
        for table_name, tmeta in table_metadata.items():
            score = 0.0
            category = tmeta.get("category", {})
            for field_name, query_value in query_attrs.items():
                if query_value is None:
                    continue
                weight = FIELD_WEIGHTS.get(field_name, 1.0)
                table_value = category.get(field_name)
                if table_value == query_value:
                    score += weight
                elif table_value is None:
                    score -= weight * 0.25
                else:
                    score -= weight * 1.0
            ranked.append((table_name, round(score, 2)))

        ranked.sort(key=lambda x: x[1], reverse=True)
        top = ranked[:top_k]

        # Format output
        descriptions = getattr(svc, "table_descriptions", {}) or {}
        lines = []
        for tname, score in top:
            desc = descriptions.get(tname, "")
            short = (desc[:160] + " …") if len(desc) > 160 else desc
            lines.append(f"  {tname}  (score {score})\n    {short}")

        resolved = {k: str(v) for k, v in query_attrs.items() if v is not None}
        return (
            f"Top {len(top)} candidates for {json.dumps(resolved)}:\n\n"
            + "\n\n".join(lines)
        )

    # ── 3. get_table_metadata ───────────────────────────────────────

    @tool
    def get_table_metadata(table_names: List[str]) -> str:
        """Return detailed metadata for one or more tables: column names
        and types, 3 sample rows, and the table's plain-English
        description.

        Call this AFTER `get_candidate_tables` and BEFORE writing SQL so
        you know the exact column names, data types, value formats, and
        units.  Never guess column names — always inspect first.

        Args:
            table_names: Table names to inspect,
                         e.g. ["hvac_chiller_90_1_2019"].
        """
        meta = svc.generate_all_metadata(
            table_filter=table_names,
            include_columns=True,
            include_sample_rows=True,
            include_descriptions=True,
            include_descriptor=False,
        )
        if not meta:
            available = svc.get_table_names(TABLE_NAMES)
            return (
                f"No metadata found for {table_names}.\n"
                f"Check spelling. Available tables include: "
                f"{', '.join(sorted(available)[:20])}"
            )

        parts = []
        for tname, tdata in meta.items():
            parts.append(f"{'=' * 60}\nTable: {tname}\n{'=' * 60}")
            if isinstance(tdata, dict):
                for section, content in tdata.items():
                    parts.append(f"\n── {section} ──\n{content}")
            else:
                parts.append(str(tdata))
        return "\n".join(parts)

    # ── 4. run_sql ──────────────────────────────────────────────────

    @tool
    def run_sql(query: str) -> str:
        """Execute a read-only SQL query against the SQLite database.

        RULES
        ─────
        • Only SELECT / WITH … SELECT — no modifications allowed.
        • Always call `get_table_metadata` first so you know the exact
          column names.  Do NOT guess.
        • If the query fails, read the error, fix the SQL, and call this
          tool again.

        Args:
            query: A valid SQLite SELECT statement.

        Returns:
            JSON-formatted result rows, or an error message.
        """
        stripped = query.strip().rstrip(";").strip()
        upper = stripped.upper()

        if not (upper.startswith("SELECT") or upper.startswith("WITH")):
            return "ERROR: Only SELECT / WITH … SELECT statements are allowed."

        forbidden = {
            "DROP", "DELETE", "UPDATE", "INSERT",
            "ALTER", "TRUNCATE", "CREATE", "REPLACE",
        }
        tokens = set(re.findall(r"\b[A-Z]{3,}\b", upper))
        if bad := tokens & forbidden:
            return f"ERROR: Forbidden keyword(s) detected: {bad}"

        try:
            with svc._connect() as conn:
                results = run_sqlite_query(stripped, conn)
        except Exception as exc:
            return f"SQL ERROR: {exc}\n\nRead the message, fix the query, and retry."

        if not results:
            return "Query executed successfully but returned 0 rows."

        if isinstance(results, list):
            n = len(results)
            preview = results[:50]
            payload = json.dumps(preview, indent=2, default=str)
            suffix = f"\n\n… and {n - 50} more rows not shown." if n > 50 else ""
            return f"{n} row(s):\n{payload}{suffix}"

        return str(results)

    # ── return all four ─────────────────────────────────────────────
    return [list_tables, get_candidate_tables, get_table_metadata, run_sql]


# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are an expert assistant for querying a building energy standards \
database (SQLite). The database contains tabulated prescriptive \
requirements for building energy codes — equipment efficiency, thermal \
envelope criteria, lighting power densities, and similar compliance \
data used in energy simulation.

## Workflow
1. **Find tables** — call `get_candidate_tables` with structured \
   descriptor attributes derived from the user's question. This is \
   almost always your first move.
2. **Inspect** — call `get_table_metadata` on the top candidate(s) to \
   see columns, types, and sample rows. Never write SQL without this.
3. **Query** — write a SELECT statement and execute it with `run_sql`.
4. **Iterate** — if the query errors or returns unexpected data, read \
   the error, adjust, and retry (up to 3 attempts).
5. **Answer** — give a clear, concise answer grounded in the results. \
   Cite the table name and any relevant column values.

## Rules
- NEVER guess column names. Always inspect metadata first.
- Use ONLY SELECT / WITH … SELECT. Never modify data.
- If you truly cannot answer, say so honestly.
- If `get_candidate_tables` returns low scores or nothing useful, fall \
  back to `list_tables` and try keyword-based reasoning.
"""
SYSTEM_PROMPT_SQL_ONLY = """\
You are an expert assistant for generating building energy standards \
database (SQLite) queries. The database contains tabulated prescriptive \
requirements for building energy codes — equipment efficiency, thermal \
envelope criteria, lighting power densities, and similar compliance \
data used in energy simulation.

## Workflow
1. **Find tables** — call `get_candidate_tables` with structured \
   descriptor attributes derived from the user's question. This is \
   almost always your first move.
2. **Inspect** — call `get_table_metadata` on the top candidate(s) to \
   see columns, types, and sample rows. Never write SQL without this.
3. **Query** — write a SELECT statement and execute it with `run_sql`.
4. **Iterate** — if the query errors or returns unexpected data, read \
   the error, adjust, and retry (up to 3 attempts).
5. **Answer** — return only the SQL query. do not return the result of the query.

## Rules
- NEVER guess column names. Always inspect metadata first.
- Use ONLY SELECT / WITH … SELECT. Never modify data.
- If you truly cannot answer, say so honestly.
- If `get_candidate_tables` returns low scores or nothing useful, fall \
  back to `list_tables` and try keyword-based reasoning.
- DO NOT REASON ABOUT THE RESULT OF THE SQL QUERY
- ONLY ANSWER WITH THE SQL QUERY
"""


# ═══════════════════════════════════════════════════════════════════════
#  AGENT
# ═══════════════════════════════════════════════════════════════════════

class BuildingEnergyAgent:
    """
    LangChain tool-calling agent for the building energy standards DB.

    Usage
    -----
    >>> with BuildingEnergyAgent() as agent:
    ...     print(agent.run("Min COP for 150-ton water-cooled chillers?"))
    """

    def __init__(
        self,
        schema_service: Optional["SchemaMetadataService"] = None,
        model: str = "claude-3-5-haiku-20241022-birthright",
        temperature: float = 0.0,
        top_k: int = 3,
    ):
        self.schema_service = schema_service or SchemaMetadataService()
        self.tools = create_tools(self.schema_service, top_k=top_k)
        self.llm = ChatAnthropic(model=model, temperature=temperature)

        self.initial_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_SQL_ONLY),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])

        self.agent = create_agent(model=model, tools=self.tools, system_prompt=SYSTEM_PROMPT_SQL_ONLY)

    def run(self, query: str, chat_history: list = None) -> str:
        """Run the agent and return the final answer string."""
        messages = list(chat_history or [])
        messages.append({"role": "user", "content": query})

        result = self.agent.invoke({"messages": messages})

        # Last AI message without tool_calls is the final answer
        for msg in reversed(result["messages"]):
            if (
                msg.type == "ai"
                and msg.content
                and not getattr(msg, "tool_calls", None)
            ):
                return msg.content

        return "No response generated."

    def run_with_steps(self, query: str, chat_history: list = None) -> Dict:
        """Run and return the answer plus every intermediate tool call."""
        messages = list(chat_history or [])
        messages.append({"role": "user", "content": query})

        result = self.agent.invoke({"messages": messages})

        steps = []
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    steps.append({
                        "type": "tool_call",
                        "tool": tc["name"],
                        "input": tc["args"],
                    })
            if msg.type == "tool":
                print(msg, msg.name, msg.content)
                steps.append({
                    "type": "tool_result",
                    "tool": msg.name,
                    "output": msg.content[:600],
                })

        answer = ""
        for msg in reversed(result["messages"]):
            if (
                msg.type == "ai"
                and msg.content
                and not getattr(msg, "tool_calls", None)
            ):
                answer = msg.content
                break

        return {"answer": answer, "steps": steps}

    def stream(self, query: str, chat_history: list = None):
        """Stream the agent's execution step by step."""
        messages = list(chat_history or [])
        messages.append({"role": "user", "content": query})

        for chunk in self.graph.stream(
            {"messages": messages},
            stream_mode="updates",
        ):
            for node_name, update in chunk.items():
                if "messages" in update:
                    for msg in update["messages"]:
                        yield {
                            "node": node_name,
                            "type": msg.type,
                            "content": getattr(msg, "content", ""),
                            "tool_calls": getattr(msg, "tool_calls", []),
                            "tool_name": getattr(msg, "name", None),
                        }

    def close(self):
        self.schema_service.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    dotenv.load_dotenv()

    with BuildingEnergyAgent() as agent:
        result = agent.run("What are the minimum visible transmittance values for skylights in climate zones 3 or 4 according to ASHRAE 90.1-2010?")

        print(result)

        # print("\n=== TOOL CALLS ===")
        # print(result["steps"])
        # for i, step in enumerate(result["steps"], 1):
        #     print(f"\n  Step {i}: {step['tool']}")
        #     print(f"  Input:  {json.dumps(step['input'], indent=2)}")
        #     print(f"  Output: {step['output'][:200]}…")

        # print("\n=== ANSWER ===")
        # print(result["answer"])