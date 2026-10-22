"""Evaluate the BESD SQL agent against a file of question / expected-answer pairs.

This is a manual, out-of-CI tool. It needs a running agent (see
``building_energy_standards_data/applications/ai_agent/build.py``) and an LLM key
in ``.env`` (``MODEL``, ``MODEL_BASE_URL``, ``API_KEY``) for the judge.

For each question it sends the query to the agent over A2A, collects the final
answer, and asks an LLM judge whether the answer agrees with ``expected_output``.

The expected outputs in ``sample_questions.json`` cite ASHRAE table numbers and
tool names (``table_filter_rows`` ...) that do not exist in this agent, so the
judge is told to score the facts and values, not table IDs or tool names.

Usage:
    uv run python evaluation/run_agent_eval.py
    uv run python evaluation/run_agent_eval.py --ids TABLE-001 TABLE-007
    uv run python evaluation/run_agent_eval.py --no-judge   # just collect answers
"""

import argparse
import asyncio
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from automa_ai.client.simple_client import SimpleClient
from dotenv import load_dotenv

from building_energy_standards_data.applications.ai_agent.ui import parse_chunk

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_QUESTIONS = EVAL_DIR / "data" / "sample_questions.json"
DEFAULT_RESULTS_DIR = EVAL_DIR / "results"

JUDGE_PROMPT = """You are grading an AI assistant that answers questions about \
building energy code requirements from a database.

Question:
{query}

Reference answer (what a correct answer should contain):
{expected}

Assistant's answer:
{answer}

Grade the assistant's answer against the reference:
- Judge the facts and numeric values (limits, efficiencies, units, conditions).
- Do NOT penalise differences in table numbers, section numbers, or tool names \
mentioned in the reference; the assistant may use different table identifiers.
- "correct": all key values and conclusions in the reference are present and right.
- "partial": some key values are right, but others are missing or wrong.
- "incorrect": the key values are wrong, missing, or the assistant did not answer.

Respond with only a JSON object: \
{{"verdict": "correct" | "partial" | "incorrect", "reasoning": "<one or two sentences>"}}"""


async def ask_agent(client: SimpleClient, query: str) -> tuple[str, str]:
    """Send one query in a fresh conversation. Returns (final_state, final_text)."""
    state, final_text = "unknown", ""
    async for chunk in client.send_streaming_message(query, uuid4().hex):
        chunk_state, text = parse_chunk(chunk)
        state = chunk_state
        if text is not None:
            final_text = text  # status text is cumulative, so replace
    return state, final_text


def build_judge():
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=os.environ["MODEL"],
        base_url=os.getenv("MODEL_BASE_URL") or None,
        api_key=os.environ["API_KEY"],
        temperature=0,
    )


def parse_verdict(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        data = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        data = {}
    verdict = data.get("verdict")
    if verdict not in {"correct", "partial", "incorrect"}:
        return {"verdict": "error", "reasoning": f"Unparseable judge output: {text}"}
    return {"verdict": verdict, "reasoning": data.get("reasoning", "")}


async def judge_answer(judge, question: dict, answer: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        query=question["query"],
        expected=question["expected_output"],
        answer=answer or "(no answer)",
    )
    response = await judge.ainvoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return parse_verdict(content)


async def run(args) -> list[dict]:
    questions = json.loads(Path(args.questions).read_text())
    if args.ids:
        questions = [q for q in questions if q["test_case_ID"] in set(args.ids)]
    if not questions:
        raise SystemExit("No questions selected.")

    client = SimpleClient(agent_url=args.url, timeout=args.timeout)
    judge = None if args.no_judge else build_judge()

    results = []
    for i, q in enumerate(questions, 1):
        qid = q["test_case_ID"]
        print(f"[{i}/{len(questions)}] {qid}: {q['query'][:90]}", flush=True)
        started = time.time()
        try:
            state, answer = await ask_agent(client, q["query"])
            error = None
        except Exception as exc:  # keep going; one failure should not stop the run
            state, answer, error = "error", "", f"{type(exc).__name__}: {exc}"
        elapsed = round(time.time() - started, 1)

        if judge is None:
            grade = {"verdict": "not_judged", "reasoning": ""}
        elif error or not answer:
            grade = {"verdict": "incorrect", "reasoning": error or "Empty answer."}
        else:
            try:
                grade = await judge_answer(judge, q, answer)
            except Exception as exc:
                grade = {
                    "verdict": "error",
                    "reasoning": f"Judge failed: {type(exc).__name__}: {exc}",
                }

        print(f"    -> {grade['verdict']} ({elapsed}s)", flush=True)
        results.append(
            {
                "test_case_ID": qid,
                "query": q["query"],
                "expected_output": q["expected_output"],
                "agent_state": state,
                "answer": answer,
                "error": error,
                "elapsed_s": elapsed,
                **grade,
            }
        )
    return results


def summarize(results: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    judged = [r for r in results if r["verdict"] in {"correct", "partial", "incorrect"}]
    score = (
        sum({"correct": 1.0, "partial": 0.5}.get(r["verdict"], 0.0) for r in judged)
        / len(judged)
        if judged
        else None
    )
    return {"total": len(results), "counts": counts, "score": score}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--questions", default=str(DEFAULT_QUESTIONS))
    parser.add_argument("--url", default="http://localhost:10000", help="A2A agent URL")
    parser.add_argument("--ids", nargs="*", help="Only run these test_case_IDs")
    parser.add_argument("--timeout", type=int, default=300, help="Per-request seconds")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM grading")
    parser.add_argument(
        "--output", help="Results JSON path (default: results/<ts>.json)"
    )
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    results = asyncio.run(run(args))
    summary = summarize(results)

    output = (
        Path(args.output)
        if args.output
        else (DEFAULT_RESULTS_DIR / f"eval_{datetime.now():%Y%m%d_%H%M%S}.json")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"summary": summary, "results": results}, indent=2))

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
    for r in results:
        print(f"{r['verdict']:<10} {r['test_case_ID']}  {r['reasoning'][:100]}")
    print(f"\nFull results: {output}")


if __name__ == "__main__":
    main()
