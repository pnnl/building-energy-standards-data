from pathlib import Path
from typing import Tuple
import logging.config
from automa_ai.common.agent_registry import A2AAgentServer, A2AServerManager
from automa_ai.common.mcp_registry import MCPServerManager
from automa_ai.network.agentic_network import MultiAgentNetwork
from automa_ai.common.setup_logging import setup_logging
import logging.config
import asyncio
from dotenv import load_dotenv

from automa_ai.common.mcp_registry import MCPServerConfig

from fine_tuning.find_table.agent.agent import build_sql_agent

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:%(name)s:%(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)



def build_network() -> Tuple[A2AServerManager, MCPServerManager]:
    sql_agent = build_sql_agent()

    mcp_manager = MCPServerManager(LOGGING_CONFIG)
    mcp_manager.add_server(sql_agent.mcp_configs["building_energy_standards"])
    a2a_manager = A2AServerManager(LOGGING_CONFIG)

    for agent_factory in [sql_agent]:
        server = A2AAgentServer(agent_factory, agent_factory.card)
        a2a_manager.add_server(server)

    return a2a_manager, mcp_manager

async def main():
    load_dotenv()

    import os
    
    a2a_manager, mcp_manager = build_network()

    await a2a_manager.start_all()
    print("A2A manager started...")
    await mcp_manager.start_all()
    print("MCP manager started...")

    await asyncio.Event().wait()

def cli():
    asyncio.run(main())

if __name__ == "__main__":
    cli()