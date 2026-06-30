from typing import List, Optional, TYPE_CHECKING

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

if TYPE_CHECKING:
    from langchain_classic.agents.agent import AgentExecutor
    from langchain.tools import BaseTool
    from langchain_core.language_models.base import BaseLanguageModel


def setup_besd_agent(
    llm: "BaseLanguageModel",
    db_uri: str,
    tools: Optional[List["BaseTool"]] = None,
    agent_type: str = "zero-shot-react-description",
    verbose: bool = True,
) -> "AgentExecutor":
    """Set up a SQL agent for the Building Energy Standards Data database.

    Creates a LangChain SQL agent that can query the OpenStudio Standards database
    using natural language. The agent will generate and execute SQL queries based
    on user questions and return the results.

    Args:
        llm: A language model instance (e.g., Claude, GPT-4).
        db_uri: Database connection URI (e.g., "sqlite:///openstudio_standards.db").
        tools: Optional list of additional LangChain tools. Defaults to None.
        agent_type: Type of agent to create. Defaults to "zero-shot-react-description".
        verbose: If True, enable verbose output for debugging. Defaults to True.

    Returns:
        An AgentExecutor instance capable of querying the database.
    """
    if tools is None:
        tools = []
    db = SQLDatabase.from_uri(db_uri)
    sql_agent = create_sql_agent(
        llm=llm,
        db=db,
        tools=tools,
        agent=agent_type,
        verbose=verbose,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": "You are an agent that queries a SQL database using valid ReAct format. Always use chain-of-thoughts to reasoning. If retrieved multiple records, list all of them in the Final Answer.",
            "format_instructions": (
                "When you need to run a query, use:\n"
                "Action: query_db\n"
                'Action Input: "SQL query here"\n\n'
                "Final Answer: the final answer to the original question\n\n"
                "Important: Always end with `Final Answer:`."
            ),
        },
    )
    return sql_agent
