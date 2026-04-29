import asyncio
from uuid import uuid4
import streamlit as st
from automa_ai.client.simple_client import SimpleClient

A2A_SERVER_URL = "http://localhost:10000"


@st.cache_resource
def get_client() -> SimpleClient:
    return SimpleClient(agent_url=A2A_SERVER_URL)


# ── Parsing ──────────────────────────────────────────────────────────
def _parts_text(parts: list[dict]) -> str:
    return "\n".join(
        p["text"] for p in parts
        if p.get("kind") == "text" and p.get("text")
    )


def parse_chunk(chunk: dict) -> tuple[str, str | None]:
    """Return (state, text). Status text is cumulative, so always REPLACE."""
    result = chunk.get("result") or {}
    kind = result.get("kind")

    match kind:
        case "task":
            for a in result.get("artifacts", []):
                if text := _parts_text(a.get("parts", [])):
                    return "completed", text
            status = result.get("status", {})
            return (
                status.get("state", "unknown"),
                _parts_text(status.get("message", {}).get("parts", [])) or None,
            )
        case "status-update":
            status = result.get("status", {})
            return (
                status.get("state", "working"),
                _parts_text(status.get("message", {}).get("parts", [])) or None,
            )
        case "artifact-update":
            return "working", _parts_text(result.get("artifact", {}).get("parts", [])) or None
        case _:
            return "unknown", None


# ── Streaming glue ───────────────────────────────────────────────────
async def stream_reply(prompt: str, ctx: str):
    """Async generator yielding (state, cumulative_text) tuples."""
    client = get_client()
    async for chunk in client.send_streaming_message(prompt, ctx):
        state, text = parse_chunk(chunk)
        if text is not None:
            yield state, text


def run_async_stream(agen):
    """Bridge an async generator into a sync one for Streamlit."""
    loop = asyncio.new_event_loop()
    try:
        while True:
            try:
                yield loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                return
    finally:
        loop.close()


# ── App ──────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="BESD Chat", page_icon="💬", layout="centered")

    with st.sidebar:
        st.title("💬 BESD Chat")
        if st.button("🗑️  New conversation"):
            st.session_state.clear()
            st.rerun()

    st.session_state.setdefault("context_id", uuid4().hex)
    st.session_state.setdefault("messages", [])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Type your message…")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        final_text = ""
        try:
            for state, text in run_async_stream(
                stream_reply(prompt, st.session_state.context_id)
            ):
                final_text = text  # cumulative, always replace
                cursor = "" if state in {"completed", "failed"} else " ▌"
                placeholder.markdown(final_text + cursor)
                if state == "failed":
                    placeholder.error(final_text)
                    break
        except Exception as exc:
            final_text = f"⚠️ {exc}"
            placeholder.error(final_text)

    if final_text:
        st.session_state.messages.append({"role": "assistant", "content": final_text})


if __name__ == "__main__":
    main()