from langchain_core.language_models import BaseLanguageModel
from langchain_core.language_models import LLM
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks.manager import CallbackManager
from langchain_experimental.sql.base import SQLDatabaseChain
from langchain.sql_database import SQLDatabase

from transformers import pipeline
from pydantic import PrivateAttr


class Text2TextLLM(LLM):
    """Wrap a HuggingFace text2text-generation pipeline for LangChain."""

    _hf_pipeline: pipeline = PrivateAttr()  # private attribute for Pydantic

    def __init__(self, hf_pipeline):
        super().__init__()
        self._hf_pipeline = hf_pipeline

    @property
    def _llm_type(self) -> str:
        return "huggingface_pipeline"

    def _call(self, prompt: str, stop=None) -> str:
        # Ensure the pipeline is called with `inputs=prompt`
        output = self._hf_pipeline([prompt], max_new_tokens=512)
        return output[0]["generated_text"]

class ToolCallLogger(BaseCallbackHandler):
    def __init__(self):
        self.steps = []

    def on_agent_action(self, action, **kwargs):
        # Logs every action the LLM tries to take
        self.steps.append({
            "tool": action.tool,
            "input": action.tool_input,
            "log": action.log
        })

    def on_agent_finish(self, finish, **kwargs):
        self.steps.append({"final_answer": finish})

logger = ToolCallLogger()
callback_manager = CallbackManager([logger])

if __name__ == "__main__":
    from building_energy_standards_data.applications.ai_agent.agent_factory import setup_besd_agent
    from building_energy_standards_data.applications.ai_agent.app import run_sql_agent_ui

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline, Text2TextGenerationPipeline
    from langchain_huggingface.llms import HuggingFacePipeline
    import torch

    import dotenv


    # Load environment variables
    dotenv.load_dotenv()


    # Load environment variables
    dotenv.load_dotenv()

    # --- Initialize the Arctic Text2SQL model ---
    model_name = "google/t5gemma-ml-ml-ul2-it"

    # Load tokenizer + model (FP16 or quantized for efficiency)
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
    )

    # Create a text-generation pipeline
    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=128,
        temperature=0.0,
        do_sample=False,
    )

    # Wrap it as a LangChain LLM so your agent can use it
    llm = HuggingFacePipeline(pipeline=pipe)

    # --- Set up your database and agent ---
    db_uri = "sqlite:///openstudio_standards.db"

    query = "List all building standards in the database."

    db = SQLDatabase.from_uri(db_uri)

    sql_chain = SQLDatabaseChain.from_llm(llm, db)

    result = sql_chain.invoke("List all building standards in the database.")

    # result = agent.invoke(query)
    # --- Launch the UI ---
    # run_sql_agent_ui(agent)