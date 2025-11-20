if __name__ == "__main__":
    from building_energy_standards_data.applications.ai_agent.agent_factory import (
        setup_besd_agent,
    )
    from building_energy_standards_data.applications.ai_agent.app import (
        run_sql_agent_ui,
    )

    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_huggingface.llms import HuggingFacePipeline
    import torch

    import dotenv

    # Load environment variables
    dotenv.load_dotenv()

    # --- Initialize the Arctic Text2SQL model ---
    model_name = "Snowflake/Arctic-Text2SQL-R1-7B"

    # Load tokenizer + model (FP16 or quantized for efficiency)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map=torch.device("mps"),
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    # Create a text-generation pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.0,
        do_sample=False,
    )

    # Wrap it as a LangChain LLM so your agent can use it
    llm = HuggingFacePipeline(pipeline=pipe)

    # --- Set up your database and agent ---
    db_uri = "sqlite:///openstudio_standards.db"
    agent = setup_besd_agent(llm, db_uri=db_uri)

    # --- Launch the UI ---
    run_sql_agent_ui(agent)
