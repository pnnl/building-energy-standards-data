import sqlglot
from sqlglot import exp
import difflib

from building_energy_standards_data.applications.ai_agent.core.utils.sql import (
    run_sqlite_query,
)


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



def diagnose_zero_rows(query: str, conn) -> str | None:
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