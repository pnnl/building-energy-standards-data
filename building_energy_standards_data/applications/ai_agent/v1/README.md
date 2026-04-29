# AI Agent for Building Energy Standards Data

This module provides an AI-powered agent interface for querying and interacting with building energy standards data using natural language. The agent utilizes LangChain and can be configured with various language models to provide intelligent responses to queries about building energy standards.

## Installation

The AI agent functionality is available as an optional dependency. Install it using pip with the `agent` extra:

```bash
pip install building-energy-standards-data[agent]
```

This will install the required dependencies including:
- langchain (>=0.3.25)
- langchain-community (>=0.3.25)
- langchain-core (>=0.3.65)

## Basic Usage

Here's a simple example of how to set up and use the AI agent:

```python
from building_energy_standards_data.applications.ai_agent.agent_factory import setup_besd_agent
from langchain_anthropic import ChatAnthropic
import dotenv

# Load environment variables (if using .env file)
dotenv.load_dotenv()

# Initialize the language model
llm = ChatAnthropic(model_name="claude-3-7-sonnet-20250219-v1-birthright")

# Set up the database URI
db_uri = "sqlite:///openstudio_standards.db"

# Create the agent
agent = setup_besd_agent(llm, db_uri=db_uri)

# Run a query
response = agent.run("What’s the minimum kW/ton for a water-cooled rotary screw in 90.1-2010?")
```

## Configuration

The `setup_custom_agent` function accepts the following parameters:

- `llm`: A BaseLanguageModel instance (required)
- `db_uri`: Database connection URI string (required)
- `tools`: Optional list of additional LangChain tools
- `agent_type`: Agent type string (default: "zero-shot-react-description")
- `verbose`: Boolean to enable verbose output (default: True)

## Environment Variables

If using the Anthropic Claude model or other API-based language models, make sure to set up the appropriate environment variables. You can use a `.env` file or set them directly in your environment:

```
ANTHROPIC_API_KEY=your_api_key_here
```