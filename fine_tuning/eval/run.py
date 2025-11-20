import csv
import json
import argparse
from typing import List
from dotenv import load_dotenv
import re
from datetime import datetime

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.models import OllamaModel


load_dotenv("../..")

evaluation_model = OllamaModel(
    model="llama3:8b",
)


def load_model(model_path: str):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "mps")
    model.to(device)
    return tokenizer, model, device

def ask_model(tokenizer, model, device, prompt: str, max_new_tokens: int = 512) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def load_csv(csv_path: str):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # expected CSV headers: question,answer,context
            rows.append({
                "question": r.get("question", "").strip(),
                "answer": r.get("answer", "").strip(),
                "context": r.get("context", "").strip(),
            })
    return rows

def run_deepeval(model_path: str, csv_path: str, out_path: str):
    tokenizer, model, device = load_model(model_path)
    rows = load_csv(csv_path)

    results = []

    metrics = [
        AnswerRelevancyMetric(threshold=0.9, model=evaluation_model, verbose_mode=True),
        FaithfulnessMetric(threshold=0.9, model=evaluation_model, verbose_mode=True),
    ]

    for i, row in enumerate(rows[:3]):
        q = row["question"]
        expected = row["answer"]
        ctx = row["context"]

        instructions = """Translate the following question to a single SQL query using ONLY the fields explicitly mentioned in the question for filtering.\nDo NOT add filters on any fields that are NOT directly mentioned in the question.\nIf a field is not mentioned, do NOT include it in the WHERE clause.\nOutput ONLY the SQL query ending with a semicolon (;).\nDo NOT include explanations, comments, or extra SQL statements."""
        full_prompt = f"{instructions}\n\nContext:\n{ctx}\n\nQuestion:\n{q}\n\nAnswer:"
        actual_output = ask_model(tokenizer, model, device, full_prompt)
        generated_sql = actual_output[len(full_prompt):]

        test_case = LLMTestCase(
            input=f"{instructions}\n\nQuestion: {q}",
            actual_output=generated_sql,
            expected_output=expected,
            retrieval_context=[ctx]
        )

        try:
            res = assert_test(test_case, metrics)
        except Exception as exc:
            res = {"error": str(exc)}

        entry = {
            "index": i,
            "question": q,
            "expected": expected,
            "actual_output": generated_sql,
            "deepeval_result": res,
        }
        results.append(entry)
        print(f"[{i}] question: {q[:80]!r} -> score summary: {res}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved results to {out_path}")


def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

def default_output_path(model_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model_name = sanitize_filename(model_name)
    return f"fine_tuning/eval/output/deepeval_results_{safe_model_name}_{timestamp}.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="meta-llama/Llama-3.2-3B", help="Path or name of your local model (transformers-compatible)")
    parser.add_argument("--csv", default="fine_tuning/dataset/final/augmented_questions_with_context.csv", help="CSV file with headers: question,answer,context")
    parser.add_argument("--out", default=None, help="Path to save results")

    args = parser.parse_args()

    if args.out is None:
        args.out = default_output_path(args.model)

    run_deepeval(args.model, args.csv, args.out)
