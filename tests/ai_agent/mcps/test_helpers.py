
from building_energy_standards_data.applications.ai_agent.mcps.helpers import (
    diagnose_zero_rows,
    _split_conjunctions,
    _extract_simple_equality,
    _get_table_name,
    _fuzzy_suggestions,
)
import sqlglot

table_name = "envelope_requirements_90_1"

class TestDiagnoseZeroRows:
    def test_returns_none_when_rows_exist(self, conn):
        sql = f"SELECT * FROM {table_name} WHERE building_category = 'Nonresidential'"
        assert diagnose_zero_rows(sql, conn) is None

    def test_returns_none_when_no_where_clause(self, conn):
        sql = f"SELECT * FROM {table_name}"
        assert diagnose_zero_rows(sql, conn) is None

    def test_unparseable_sql_returns_none(self, conn):
        assert diagnose_zero_rows("this is not sql", conn) is None

    def test_missing_value_gives_hint_with_failing_predicate(self, conn):
        sql = f"SELECT * FROM {table_name} WHERE building_category = 'NotARealCategory'"
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "removes all rows" in hint
        assert "building_category" in hint
        assert "NotARealCategory" in hint

    def test_missing_value_lists_sample_existing_values(self, conn):
        sql = f"SELECT * FROM {table_name} WHERE building_category = 'NotARealCategory'"
        hint = diagnose_zero_rows(sql, conn)
        assert "Top existing values" in hint
        assert "Nonresidential" in hint

    def test_fuzzy_suggestion_returned_for_typo(self, conn):
        # 'Nonresdential' is a typo for 'Nonresidential'
        sql = f"SELECT * FROM {table_name} WHERE building_category = 'Nonresdential'"
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "Did you mean" in hint
        assert "Nonresidential" in hint

    def test_finds_failing_predicate_in_conjunction(self, conn):
        # first predicate matches, second fails
        sql = (
            f"SELECT * FROM {table_name} "
            "WHERE building_category = 'Nonresidential' AND climate_zone_set = 'ClimateZone 9Z'"
        )
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "climate_zone_set" in hint
        assert "ClimateZone 9Z" in hint
        # shouldn't blame the passing predicate
        assert "building_category" not in hint.split("removes all rows")[0] or "climate_zone" in hint

    def test_non_equality_predicate_returns_generic_hint(self, conn):
        sql = f"SELECT * FROM {table_name} WHERE assembly_maximum_u_value > 9000"
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "eliminates all rows" in hint

    def test_equality_with_existing_value_but_combined_filter_fails(self, conn):
        # value exists but combined with another predicate gives zero rows
        sql = (
            f"SELECT * FROM {table_name} "
            "WHERE intended_surface_type = 'ExteriorDoor' AND maximum_percent_of_surface = 0"
        )
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "eliminates all rows" in hint

    def test_numeric_equality_no_fuzzy_suggestions(self, conn):
        sql = f"SELECT * FROM {table_name} WHERE assembly_maximum_u_value = 0.0001"
        hint = diagnose_zero_rows(sql, conn)
        assert hint is not None
        assert "eliminates all rows" in hint


class TestHelpers:
    def test_split_conjunctions_single(self):
        parsed = sqlglot.parse_one("SELECT * FROM t WHERE a = 1")
        where = parsed.args["where"].this
        preds = _split_conjunctions(where)
        assert len(preds) == 1

    def test_split_conjunctions_multiple(self):
        parsed = sqlglot.parse_one(
            "SELECT * FROM t WHERE a = 1 AND b = 2 AND c = 3"
        )
        where = parsed.args["where"].this
        preds = _split_conjunctions(where)
        assert len(preds) == 3

    def test_extract_simple_equality_string(self):
        parsed = sqlglot.parse_one("SELECT * FROM t WHERE col = 'foo'")
        pred = parsed.args["where"].this
        assert _extract_simple_equality(pred) == ("col", "foo")

    def test_extract_simple_equality_reversed(self):
        parsed = sqlglot.parse_one("SELECT * FROM t WHERE 'foo' = col")
        pred = parsed.args["where"].this
        assert _extract_simple_equality(pred) == ("col", "foo")

    def test_extract_simple_equality_numeric_returns_none(self):
        parsed = sqlglot.parse_one("SELECT * FROM t WHERE col = 123")
        pred = parsed.args["where"].this
        assert _extract_simple_equality(pred) is None

    def test_extract_simple_equality_non_eq_returns_none(self):
        parsed = sqlglot.parse_one("SELECT * FROM t WHERE col > 1")
        pred = parsed.args["where"].this
        assert _extract_simple_equality(pred) is None

    def test_get_table_name(self):
        parsed = sqlglot.parse_one("SELECT * FROM buildings WHERE a = 1")
        assert _get_table_name(parsed) == "buildings"

    def test_fuzzy_match_exact_match_returned(self, conn):
        result = _fuzzy_suggestions(table=table_name, col="building_category", val="Residential", conn=conn)
        assert "Residential" in result

    def test_fuzzy_match_single_char_typo_matches(self, conn):
        # "Resdential" → "Residential"
        result = _fuzzy_suggestions(table=table_name, col="building_category", val="Resdential", conn=conn)
        assert "Residential" in result

    def test_fuzzy_match_leading_trailing_whitespace_ignored(self, conn):
        result = _fuzzy_suggestions(table=table_name, col="building_category", val="  Residential  ", conn=conn)
        assert "Residential" in result

    def test_fuzzy_matchcompletely_unrelated_value_returns_empty(self, conn):
        result = _fuzzy_suggestions(
            table=table_name, col="building_category", val="xyzabc123", conn=conn
        )
        assert result == []

    def test_fuzzy_match_empty_string_returns_empty_or_no_close(self, conn):
        result = _fuzzy_suggestions(table=table_name, col="building_category", val="", conn=conn)
        assert result == []

    def test_fuzzy_match_limit(self, conn):
        result = _fuzzy_suggestions(
            table=table_name, col="climate_zone_set", val="ClimateZone", conn=conn
        )
        assert len(result) == 5