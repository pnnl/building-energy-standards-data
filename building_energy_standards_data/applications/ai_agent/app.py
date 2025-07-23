import streamlit as st
from langchain.agents import AgentExecutor


def run_sql_agent_ui(agent: AgentExecutor):
    st.title("BESD Agent Interface")

    user_query = st.text_area("Enter your question")

    if st.button("Run Query"):
        if not user_query.strip():
            st.warning("Please enter a query.")
            return

        try:

            with st.spinner("Running query..."):
                response = agent.run(user_query)

            st.write("**Response:**")
            st.write(response)

        except Exception as e:
            st.error(f"Error: {e}")
