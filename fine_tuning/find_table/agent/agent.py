import json
import os

from pathlib import Path

from automa_ai.common.mcp_registry import MCPServerConfig

from fine_tuning.find_table.agent.prompts import AGENT_PROMPT
import json
from pathlib import Path
from a2a.types import AgentCard, AgentCapabilities

from fine_tuning.find_table.agent.mcps.server import serve as serve_mcp
import json
from pathlib import Path
from a2a.types import AgentCard
from automa_ai.agents import GenericLLM, GenericAgentType
from automa_ai.agents.agent_factory import AgentFactory

from fine_tuning.find_table.agent.prompts import AGENT_PROMPT

"""
agent.py — LangChain agent that discovers tools via MCP.

The agent no longer imports any tool code.  Instead it launches the
MCP server as a subprocess and loads tools over the MCP protocol.
"""

import json
from pathlib import Path

def build_sql_agent() -> AgentFactory:
    BASE_DIR = Path(__file__).resolve().parent
    AGENT_CARD_PATH = BASE_DIR / "agent_cards" / "sql_agent.json"
    card = AgentCard(**json.loads(AGENT_CARD_PATH.read_text()), capabilities=AgentCapabilities(streaming=True))

    mcp_server_config = MCPServerConfig(
            name="building_energy_standards",
            host="127.0.0.1",
            port=11000,
            serve=serve_mcp,
            transport="sse",
        )
    
    print(mcp_server_config)

    return AgentFactory(
        card=card,
        instructions=AGENT_PROMPT,
        agent_type=GenericAgentType.LANGGRAPHCHAT,
        chat_model=GenericLLM.CLAUDE,
        model_name=os.getenv("MODEL"),
        model_base_url=os.getenv("MODEL_BASE_URL"),
        mcp_configs={mcp_server_config.name: mcp_server_config},
        api_key=os.getenv("API_KEY"),
        debug=True
    )