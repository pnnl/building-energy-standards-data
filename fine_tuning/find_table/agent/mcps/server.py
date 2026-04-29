import json
import re
from typing import Optional

from fastmcp import FastMCP

from fine_tuning.find_table.pipeline.lookup_pipeline import TABLE_NAMES

from fine_tuning.find_table.table_matching.table_metadata import SchemaMetadataService
from fine_tuning.find_table.table_matching.types import TableDescriptor, Domain, Topic, System, SubSystem, StandardFamily, CompliancePath
from fine_tuning.find_table.utils import (
    get_field_weights,
    run_sqlite_query,
)

import sqlglot
from sqlglot import exp


import difflib


def _normalize(s: str) -> str:
    return s.lower().strip()


def _fuzzy_suggestions(table: str, col: str, val: str, conn, limit: int = 5):
    """Return close matches for a value from a column."""
    try:
        rows = run_sqlite_query(
            f"""
            SELECT CAST({col} AS TEXT) AS v, COUNT(*) as c
            FROM {table}
            GROUP BY CAST({col} AS TEXT)
            ORDER BY c DESC
            LIMIT 500
            """,
            conn,
        )
    except Exception:
        return []

    candidates = [r["v"] for r in rows if r["v"]]

    norm_val = _normalize(val)
    norm_map = {c: _normalize(c) for c in candidates}

    matches = difflib.get_close_matches(
        norm_val,
        list(norm_map.values()),
        n=limit,
        cutoff=0.5,
    )

    # map normalized back to original values
    result = []
    for m in matches:
        for original, normed in norm_map.items():
            if normed == m:
                result.append(original)
                break

    return result

def _split_conjunctions(where_expr: exp.Expression) -> list[exp.Expression]:
    """Flatten AND conditions into a list."""
    if isinstance(where_expr, exp.And):
        return _split_conjunctions(where_expr.left) + _split_conjunctions(where_expr.right)
    return [where_expr]


def _remove_where(parsed: exp.Expression) -> exp.Expression:
    """Return a copy of the query without WHERE."""
    parsed = parsed.copy()
    if isinstance(parsed, exp.Select):
        parsed.set("where", None)
    return parsed


def _with_where(parsed: exp.Expression, conditions: list[exp.Expression]) -> exp.Expression:
    """Attach a WHERE clause with given conditions."""
    parsed = parsed.copy()
    if not conditions:
        parsed.set("where", None)
        return parsed

    cond = conditions[0]
    for c in conditions[1:]:
        cond = exp.and_(cond, c)

    parsed.set("where", exp.Where(this=cond))
    return parsed


def _count_rows(sql: str, conn) -> int:
    q = f"SELECT COUNT(*) as c FROM ({sql})"
    result = run_sqlite_query(q, conn)
    return result[0]["c"] if result else 0


def _find_failing_predicate(parsed: exp.Expression, conn) -> exp.Expression | None:
    """Return the predicate that reduces results to zero."""
    where = parsed.args.get("where")
    if not where:
        return None

    predicates = _split_conjunctions(where.this)
    base = _remove_where(parsed)

    working: list[exp.Expression] = []

    for pred in predicates:
        test_conditions = working + [pred]
        test_query = _with_where(base, test_conditions).sql()

        if _count_rows(test_query, conn) == 0:
            return pred

        working.append(pred)

    return None


def _extract_simple_equality(pred: exp.Expression) -> tuple[str, str] | None:
    """Return (column, value) if predicate is col = 'value'."""
    if isinstance(pred, exp.EQ):
        left, right = pred.left, pred.right

        if isinstance(left, exp.Column) and isinstance(right, exp.Literal) and right.is_string:
            return left.name, right.this

        if isinstance(right, exp.Column) and isinstance(left, exp.Literal) and left.is_string:
            return right.name, left.this

    return None


def _get_table_name(parsed: exp.Expression) -> str | None:
    """Best-effort: first table in FROM."""
    # print(parsed.args)

    from_ = parsed.args.get("from_")
    if not from_:
        return None

    table = from_.find(exp.Table)
    return table.name if table else None



def _diagnose_zero_rows(query: str, conn) -> str | None:
    try:
        parsed = sqlglot.parse_one(query)
    except Exception:
        return None  # can't parse → give up safely

    failing_pred = _find_failing_predicate(parsed, conn)
    if not failing_pred:
        return None

    eq = _extract_simple_equality(failing_pred)
    table = _get_table_name(parsed)

    if eq and table:
        col, val = eq

        try:
            exists = run_sqlite_query(
                f"SELECT 1 FROM {table} WHERE CAST({col} AS TEXT) = ? LIMIT 1",
                conn,
                params=(val,),
            )
        except Exception:
            exists = None

        if not exists:
            # --- NEW: fuzzy suggestions ---
            suggestions = _fuzzy_suggestions(table, col, val, conn)

            try:
                samples = run_sqlite_query(
                    f"""
                    SELECT CAST({col} AS TEXT) AS v, COUNT(*) AS c
                    FROM {table}
                    GROUP BY CAST({col} AS TEXT)
                    ORDER BY c DESC
                    LIMIT 5
                    """,
                    conn,
                )
                sample_vals = [r["v"] for r in samples]
            except Exception:
                sample_vals = []

            hint = (
                f"HINT: Filter `{failing_pred.sql()}` removes all rows.\n"
                f"Value '{val}' does not exist in column `{col}`."
            )

            if suggestions:
                hint += f"\nDid you mean: {suggestions}?"

            if sample_vals:
                hint += f"\nTop existing values: {sample_vals}"

            return hint

        return f"HINT: Filter `{failing_pred.sql()}` removes all rows."

    return f"HINT: Predicate `{failing_pred.sql()}` eliminates all rows."


def _resolve_enum(enum_cls, value):
    """Try to coerce *value* into an enum member; return None on failure."""
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except (ValueError, KeyError):
        pass
    # Try name-based lookup (case-insensitive)
    for member in enum_cls:
        if member.name.lower() == str(value).lower():
            return member
    return None

def create_mcp_server(
    schema_service: "SchemaMetadataService",
    name="building-energy-standards",
    host="127.0.0.1",
    port=11000
) -> FastMCP:
    """
    Build and return a fully-configured ``FastMCP`` server with four
    tools that all close over the shared *schema_service*.
    """

    mcp = FastMCP(
        name=name,
    )

    svc = schema_service

    @mcp.tool(
        name="list_tables",
        description=(
            "List every table in the building energy standards database. "
            "Returns each table name with a short description.  Use this "
            "to get a broad overview of what data is available *before* "
            "narrowing your search with `get_candidate_tables`."
        ),
    )
    def list_tables() -> str:
        """List every table in the building energy standards database."""
        tables = svc.get_table_names(TABLE_NAMES)
        descriptions = getattr(svc, "table_descriptions", {}) or {}

        lines: list[str] = []
        for t in sorted(tables):
            desc = descriptions.get(t, "")
            short = (desc[:200] + " ...") if len(desc) > 200 else desc
            lines.append(f"* {t}  -  {short}")

        return f"{len(tables)} tables available:\n\n" + "\n".join(lines)

    @mcp.tool(
        name="get_candidate_tables",
        description=(
            "Find the most relevant tables by matching structured "
            "descriptor attributes against every table in the catalogue.\n"
            "\n"
            "-- WHEN TO CALL --\n"
            "This should be your FIRST tool call for most questions.  "
            "Translate the user's intent into descriptor fields, and this "
            "tool will return a ranked shortlist.\n"
            "\n"
            "-- HOW SCORING WORKS --\n"
            "Each field has a weight.  An exact match adds +weight, a "
            "mismatch subtracts -weight, and a null query field is "
            "ignored (no penalty).\n"
            "Field weights (highest -> lowest):\n"
            "    system          5.0  <- strongest signal\n"
            "    sub_system      3.0\n"
            "    standard_year   2.0\n"
            "    topic           1.5\n"
            "    domain          1.0\n"
            "    standard_family 1.0\n"
            "    compliance_path 1.0\n"
            "\n"
            "-- STRATEGY --\n"
            "* Always set `domain`.\n"
            "* Set `system` whenever the user mentions equipment - it "
            "dominates the ranking.\n"
            "* Leave a field null when uncertain - a null is neutral, "
            "but a wrong value is heavily penalised.\n"
            "* Fill as many fields as possible and all others null. \n"
            "\n"
            "-- NEXT STEP --\n"
            "Call `get_table_metadata` on the top result(s) to inspect "
            "columns and sample rows before writing SQL."
        ),
    )
    def get_candidate_tables(
        domain: Domain,
        topic: Topic = None,
        system: Optional[System] = None,
        sub_system: Optional[SubSystem] = None,
        standard_family: Optional[StandardFamily] = None,
        standard_year: Optional[int] = None,
        compliance_path: Optional[CompliancePath] = None,
    ) -> str:
        """Find the most relevant tables for a query by scoring
        descriptor attributes.

        Args:
            domain: The broad domain, e.g. "commercial", "residential".
            topic: High-level topic such as "envelope", "lighting",
                   "hvac", "swh".
            system: Equipment / system type, e.g. "chiller",
                    "heat_pump".  Strongest ranking signal.
            sub_system: Sub-system refinement,
                        e.g. "air_cooled_chiller".
            standard_family: Standard family, e.g. "ashrae_90_1",
                             "iecc".
            standard_year: Edition year, e.g. 2019.
            compliance_path: Compliance path, e.g. "prescriptive",
                             "performance".
        """
        query_attrs = {
            "domain":          _resolve_enum(Domain, domain),
            "topic":           _resolve_enum(Topic, topic),
            "system":          _resolve_enum(System, system),
            "sub_system":      _resolve_enum(SubSystem, sub_system),
            "standard_family": _resolve_enum(StandardFamily, standard_family),
            "standard_year":   standard_year,
            "compliance_path": _resolve_enum(CompliancePath, compliance_path),
        }

        table_metadata = svc.generate_all_metadata(
            table_filter=TABLE_NAMES,
            include_columns=False,
            include_descriptor=True,
        )

        FIELD_WEIGHTS = get_field_weights(TableDescriptor)
        ranked: list[tuple[str, float]] = []

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
        top = ranked[:3]

        descriptions = getattr(svc, "table_descriptions", {}) or {}
        lines: list[str] = []
        for tname, score in top:
            desc = descriptions.get(tname, "")
            short = (desc[:160] + " ...") if len(desc) > 160 else desc
            lines.append(f"  {tname}  (score {score})\n    {short}")

        resolved = {
            k: str(v) for k, v in query_attrs.items() if v is not None
        }
        return (
            f"Top {len(top)} candidates for {json.dumps(resolved)}:\n\n"
            + "\n\n".join(lines)
        )

    @mcp.tool(
        name="get_table_metadata",
        description=(
            "Return detailed metadata for one or more tables: column "
            "names and types, 3 sample rows, and the table's "
            "plain-English description.\n"
            "\n"
            "Call this AFTER `get_candidate_tables` and BEFORE writing "
            "SQL so you know the exact column names, data types, value "
            "formats, and units.  Never guess column names - always "
            "inspect first."
        ),
    )
    def get_table_metadata(table_names: list[str]) -> str:
        """Inspect schema, sample rows, and description for the given
        tables.

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

        parts: list[str] = []
        for tname, tdata in meta.items():
            parts.append(f"{'=' * 60}\nTable: {tname}\n{'=' * 60}")
            if isinstance(tdata, dict):
                for section, content in tdata.items():
                    parts.append(f"\n-- {section} --\n{content}")
            else:
                parts.append(str(tdata))

        return "\n".join(parts)

    @mcp.tool(
        name="run_sql",
        description=(
            "Execute a read-only SQL query against the SQLite database.\n"
            "\n"
            "RULES\n"
            "-----\n"
            "* Only SELECT / WITH ... SELECT - no modifications allowed.\n"
            "* Always call `get_table_metadata` first so you know the "
            "exact column names.  Do NOT guess.\n"
            "* If the query fails, read the error, fix the SQL, and "
            "call this tool again."
        ),
    )
    def run_sql(query: str) -> str:
        stripped = query.strip().rstrip(";").strip()
        upper = stripped.upper()
        if not (upper.startswith("SELECT") or upper.startswith("WITH")):
            return "ERROR: Only SELECT / WITH ... SELECT statements are allowed."

        forbidden = {"DROP", "DELETE", "UPDATE", "INSERT",
                    "ALTER", "TRUNCATE", "CREATE", "REPLACE"}
        if bad := set(re.findall(r"\b[A-Z]{3,}\b", upper)) & forbidden:
            return f"ERROR: Forbidden keyword(s) detected: {bad}"

        try:
            with svc._connect() as conn:
                results = run_sqlite_query(stripped, conn)

                if not results:
                    hint = _diagnose_zero_rows(stripped, conn)
                    base = "Query executed successfully but returned 0 rows."
                    return f"{base}\n\n{hint}" if hint else base
        except Exception as exc:
            return f"SQL ERROR: {exc}\n\nRead the message, fix the query, and retry."

        n = len(results)
        preview = results[:50]
        payload = json.dumps(preview, indent=2, default=str)
        suffix = f"\n\n... and {n - 50} more rows not shown." if n > 50 else ""
        return f"{n} row(s):\n{payload}{suffix}"
    
    @mcp.tool(
        name="get_unique_values",
        description=(
            "Show up to N distinct values from one or more columns in a given table "
            "(optionally ordered by frequency). Validates table/columns first."
        ),
    )
    def get_unique_values(
        table: str,
        column_names: list[str],
        limit: int = 10,
        order_by_count: bool = True,
        where: Optional[str] = None,  # optional SQL predicate, e.g. "standard_year = 2019"
    ) -> str:
        # ── Normalize / clamp inputs ─────────────────────────────────────
        limit = max(1, min(int(limit), 50))
        if isinstance(column_names, str):           # be forgiving if a single str slips in
            column_names = [column_names]
        if not column_names:
            return "ERROR: `column_names` must be a non-empty list."

        # ── Validate table ───────────────────────────────────────────────
        meta = svc.generate_all_metadata(
            table_filter=[table],
            include_columns=True,
            include_sample_rows=False,
            include_descriptions=False,
            include_descriptor=False,
        )
        if table not in meta:
            available = svc.get_table_names(TABLE_NAMES)
            return (
                f"ERROR: Unknown table '{table}'.\n"
                f"Example tables: {', '.join(sorted(available)[:20])}"
            )

        # ── Extract known columns for this table ─────────────────────────
        columns_section = meta[table].get("columns")
        if isinstance(columns_section, dict):
            colnames = set(columns_section.keys())
        else:
            colnames = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", str(columns_section or "")))

        # ── Validate every requested column up front ─────────────────────
        unknown = [c for c in column_names if c not in colnames]
        if unknown:
            return (
                f"ERROR: Unknown column(s) {unknown} in table '{table}'.\n"
                f"Known columns (sample): {', '.join(sorted(colnames)[:40])}"
            )

        # ── Run one query per column ─────────────────────────────────────
        order_clause = "ORDER BY cnt DESC, value ASC" if order_by_count else "ORDER BY value ASC"
        where_clause = f"WHERE {where}" if where else ""

        output: dict[str, object] = {}
        try:
            with svc._connect() as conn:
                for col in column_names:
                    sql = f"""
                    SELECT CAST({col} AS TEXT) AS value, COUNT(*) AS cnt
                    FROM {table}
                    {where_clause}
                    GROUP BY CAST({col} AS TEXT)
                    {order_clause}
                    LIMIT {limit}
                    """.strip()
                    try:
                        rows = run_sqlite_query(sql, conn)
                        output[col] = rows if rows else "No values found (0 rows)."
                    except Exception as exc:
                        output[col] = f"SQL ERROR: {exc}"
        except Exception as exc:
            return f"SQL ERROR (connection): {exc}"

        header = f"Up to {limit} distinct values per column for table `{table}`:"
        return header + "\n" + json.dumps(output, indent=2, default=str)
    
    return mcp

def serve(host, port, transport):

    schema_service = SchemaMetadataService()

    server = create_mcp_server(schema_service, name="building_energy_standards_database", host=host, port=port)

    server.run(transport=transport, host=host, port=port)

if __name__ == "__main__":
    serve("127.0.0.1", 11000, "sse")