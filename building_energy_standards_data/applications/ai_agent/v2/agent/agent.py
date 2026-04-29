import json
import os
from pathlib import Path

from a2a.types import AgentCard, AgentCapabilities
from automa_ai.common.mcp_registry import MCPServerConfig
from automa_ai.agents import GenericLLM, GenericAgentType
from automa_ai.agents.agent_factory import AgentFactory

from building_energy_standards_data.applications.ai_agent.v2.agent.prompts import AGENT_PROMPT
from building_energy_standards_data.applications.ai_agent.v2.mcps.server import serve as serve_mcp


def build_sql_agent() -> AgentFactory:
    here = Path(__file__).resolve()
    AGENT_CARD_PATH = here.parent / "agent_cards" / "sql_agent.json"
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