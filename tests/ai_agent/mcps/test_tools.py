import json
import sqlite3
import pytest
import pytest_asyncio

from mcp.server.fastmcp import FastMCP

# Adjust to your actual import path
from building_energy_standards_data.applications.ai_agent.core.models.types import Domain, StandardFamily
from building_energy_standards_data.applications.ai_agent.core.services.schema_metadata_service import SchemaMetadataService
from building_energy_standards_data.applications.ai_agent.mcps.tools import (
    register_tools,
)

@pytest.fixture
def svc():
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
        result = await call_tool(mcp, "get_candidate_tables", {"domain": Domain.ENVELOPE})
        assert result.startswith("Top 5 candidates")
        assert all(t in result for t in ["envelope_requirements_90_1", "envelope_requirements_90_1_prm", "envelope_requirements_IECC"])

    async def test_standard_year_disambiguates_between_similar_tables(self, mcp):
        # Both chiller tables match system=chiller; year decides the winner.
        out = await call_tool(
            mcp,
            "get_candidate_tables",
            {
                "domain": Domain.ENVELOPE,
                "standard_family": StandardFamily.ASHRAE_90_1
            },
        )
        first_block = out.split("\n\n")[1]
        assert "envelope_requirements_90_1" in first_block

        out = await call_tool(
            mcp,
            "get_candidate_tables",
            {
                "domain": Domain.ENVELOPE,
                "standard_family": StandardFamily.IECC
            },
        )
        first_block = out.split("\n\n")[1]
        assert "envelope_requirements_IECC" in first_block