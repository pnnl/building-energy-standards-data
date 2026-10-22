import json
import sqlite3
import pytest
import pytest_asyncio

from mcp.server.fastmcp import FastMCP

# Adjust to your actual import path
from building_energy_standards_data.applications.ai_agent.config import TABLE_NAMES
from building_energy_standards_data.applications.ai_agent.core.models.types import (
    Domain,
    StandardFamily,
)
from building_energy_standards_data.applications.ai_agent.core.services.schema_metadata_service import (
    SchemaMetadataService,
)
from building_energy_standards_data.applications.ai_agent.mcps.tools import (
    register_tools,
)


@pytest.fixture
def svc(conn):
    return SchemaMetadataService()


@pytest.fixture
def mcp(svc):
    server = FastMCP("test-server")
    register_tools(server, svc)
    return server


async def call_tool(mcp: FastMCP, name: str, arguments: dict) -> str:
    result = await mcp.call_tool(name, arguments)
    # Newer FastMCP returns (content, structured); older returns just content
    content = result[0] if isinstance(result, tuple) else result
    texts = []
    for block in content:
        text = getattr(block, "text", None)
        if text is not None:
            texts.append(text)
    return "\n".join(texts)


@pytest.mark.asyncio
class TestRegistration:
    async def test_tools_discoverable(self, mcp):
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert {
            "list_tables",
            "run_sql",
        }.issubset(names)

    async def test_tool_descriptions_present(self, mcp):
        tools = await mcp.list_tools()
        for t in tools:
            assert t.description and len(t.description) > 10


@pytest.mark.asyncio
class TestListTables:
    async def test_lists_all_tables(self, mcp):
        result = await call_tool(mcp, "list_tables", {})
        assert "envelope_requirements_90_1" in result

    async def test_lists_tables_with_descriptions(self, mcp):
        result = await call_tool(mcp, "list_tables_with_descriptions", {})
        assert "envelope_requirements_90_1" in result
        assert "The `envelope_requirements_90_1` table stores prescriptive" in result


@pytest.mark.asyncio
class TestGetCandidateTables:
    async def test_returns_header_with_top_n(self, mcp):
        result = await call_tool(
            mcp, "get_candidate_tables", {"domain": Domain.ENVELOPE}
        )
        assert result.startswith("Top 6 candidates")
        assert all(
            t in result
            for t in [
                "envelope_requirements_90_1",
                "envelope_requirements_90_1_prm",
                "envelope_requirements_IECC",
                "envelope_requirements_189_1",
            ]
        )

    async def test_standard_year_disambiguates_between_similar_tables(self, mcp):
        # The standard family selects the matching envelope table. Tables that tie on
        # score (e.g. thermal bridging) may be listed first, so only check presence.
        out = await call_tool(
            mcp,
            "get_candidate_tables",
            {"domain": Domain.ENVELOPE, "standard_family": StandardFamily.ASHRAE_90_1},
        )
        assert "envelope_requirements_90_1" in out
        assert "envelope_requirements_IECC" not in out

        out = await call_tool(
            mcp,
            "get_candidate_tables",
            {"domain": Domain.ENVELOPE, "standard_family": StandardFamily.IECC},
        )
        assert "envelope_requirements_IECC" in out
        assert "envelope_requirements_90_1" not in out

    async def test_ventilation_domain_finds_ventilation_tables(self, mcp):
        out = await call_tool(
            mcp,
            "get_candidate_tables",
            {
                "domain": Domain.VENTILATION,
                "standard_family": StandardFamily.ASHRAE_62_1,
            },
        )
        assert "level_3_ventilation_62_1_2022" in out
        assert "level_3_lighting" not in out


def test_every_allowlisted_table_has_a_known_domain(svc):
    unknown = [
        t for t in TABLE_NAMES if svc.parse_table_name(t).domain == Domain.UNKNOWN
    ]
    assert unknown == []
