import streamlit as st
from langchain_classic.agents.agent import AgentExecutor
from langchain_core.messages import AIMessage


def run_sql_agent_ui(agent: AgentExecutor):
    st.title("BESD Agent Interface")

    user_query = st.text_area("Enter your question")

    if st.button("Run Query"):
        if not user_query.strip():
            st.warning("Please enter a query.")
            return

        try:

            with st.spinner("Running query..."):
                for item in agent.stream(user_query):
                    if "messages" in item:
                        message = item["messages"][-1]
                        if isinstance(message, AIMessage) and message.content:
                            content = message.content.strip()
                            # Process line-by-line
                            for line in content.splitlines():
                                line = line.strip()
                                if line.startswith("Action:"):
                                    st.markdown(
                                        f'<div style="background-color:#fff3cd;padding:8px;border-radius:6px;">{line}</div>',
                                        unsafe_allow_html=True,
                                    )
                                elif line.startswith("Action Input:"):
                                    st.markdown(
                                        f'<div style="background-color:#d1ecf1;padding:8px;border-radius:6px;">{line}</div>',
                                        unsafe_allow_html=True,
                                    )
                                elif line.startswith("Final Answer:"):
                                    st.markdown(
                                        f'<div style="background-color:#d4edda;padding:8px;border-radius:6px;"><strong>{line}</strong></div>',
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    st.markdown(
                                        f'<div style="background-color:#f8f9fa;padding:8px;border-radius:6px;">{line}</div>',
                                        unsafe_allow_html=True,
                                    )

        except Exception as e:
            st.error(f"Error: {e}")