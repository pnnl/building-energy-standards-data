from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.tools.base import BaseTool
from langchain_core.language_models.base import BaseLanguageModel
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent


def setup_besd_agent(
    llm: BaseLanguageModel,
    db_uri: str,
    tools: Optional[List[BaseTool]] = [],
    agent_type: str = "zero-shot-react-description",
    verbose: bool = True,
) -> AgentExecutor:
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
