"""
Synthetic Dataset Generator for SQL Question-Query Pairs
Generates new training examples by analyzing existing patterns and creating variations
"""

import sqlite3
import csv
import json
import re
from collections import Counter
from typing import List, Dict
import random

# Configuration
EXISTING_CSV = "manual_std_queries.csv"
OUTPUT_CSV = "updated_building_queries.csv"
SQLITE_DB = "openstudio_standards.db"
TARGET_COUNT = 1000  # Total examples you want


def load_existing_examples(csv_path: str) -> List[Dict[str, str]]:
    """Load existing question-query pairs from CSV"""
    examples = []
    with open(csv_path, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("question") and row.get("answer"):  # Skip empty rows
                examples.append(
                    {
                        "question": row["question"].strip(),
                        "query": row["answer"].strip(),
                    }
                )
    return examples


def get_database_schema(db_path: str) -> Dict[str, List[str]]:
    """Extract schema information from SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        schema[table] = columns

    conn.close()
    return schema


def analyze_patterns(examples: List[Dict[str, str]]) -> Dict:
    """Analyze patterns in existing examples to guide generation"""
    patterns = {
        "tables_used": Counter(),  # Track frequency of table usage
        "column_filters": Counter(),  # Track commonly filtered columns
        "aggregations": Counter(),  # Track aggregation types with counts
        "join_patterns": [],  # Track multi-table queries
        "comparison_examples": [],  # Store comparison question examples
        "question_starters": Counter(),  # Track how questions begin
        "complexity_distribution": {  # Track query complexity
            "simple": 0,  # Single table, no aggregation
            "moderate": 0,  # Single table with aggregation OR multiple tables
            "complex": 0,  # Multiple tables with aggregation
        },
    }

    for ex in examples:
        query = ex["query"]
        query_upper = query.upper()
        question = ex["question"]

        # === EXTRACT TABLES ===
        # Handle single table queries
        from_match = re.search(r"FROM\s+(\w+)", query_upper, re.IGNORECASE)
        if from_match:
            table = from_match.group(1).lower()
            patterns["tables_used"][table] += 1

        # Handle JOINs (multiple tables)
        join_matches = re.findall(r"JOIN\s+(\w+)", query_upper, re.IGNORECASE)
        if join_matches:
            for table in join_matches:
                patterns["tables_used"][table.lower()] += 1
            patterns["join_patterns"].append(
                {
                    "question": question,
                    "tables": [from_match.group(1).lower() if from_match else None]
                    + [t.lower() for t in join_matches],
                }
            )

        # === EXTRACT FILTERED COLUMNS ===
        # Find columns in WHERE clauses
        where_match = re.search(
            r"WHERE\s+(.+?)(?:GROUP BY|ORDER BY|LIMIT|$)",
            query_upper,
            re.IGNORECASE | re.DOTALL,
        )
        if where_match:
            where_clause = where_match.group(1)
            # Extract column names before comparison operators
            column_matches = re.findall(
                r"(\w+)\s*(?:=|>|<|>=|<=|!=|LIKE|IN)", where_clause, re.IGNORECASE
            )
            for col in column_matches:
                patterns["column_filters"][col.lower()] += 1

        # === DETECT AGGREGATIONS ===
        agg_types = []
        if re.search(r"MAX\s*\(", query_upper):
            agg_types.append("MAX")
        if re.search(r"MIN\s*\(", query_upper):
            agg_types.append("MIN")
        if re.search(r"COUNT\s*\(", query_upper):
            agg_types.append("COUNT")
        if re.search(r"AVG\s*\(", query_upper):
            agg_types.append("AVG")
        if re.search(r"SUM\s*\(", query_upper):
            agg_types.append("SUM")
        if "GROUP BY" in query_upper:
            agg_types.append("GROUP_BY")

        for agg in agg_types:
            patterns["aggregations"][agg] += 1

        # === IDENTIFY COMPARISON QUESTIONS ===
        comparison_keywords = [
            "compare",
            "differ",
            "difference",
            "versus",
            "vs",
            "between",
            "higher than",
            "lower than",
            "greater than",
        ]
        if any(keyword in question.lower() for keyword in comparison_keywords):
            patterns["comparison_examples"].append(
                {"question": question, "query": query}
            )

        # === EXTRACT QUESTION STARTERS ===
        # Get first 2-3 words of question
        starter = " ".join(question.split()[:3]).lower()
        patterns["question_starters"][starter] += 1

        # === DETERMINE COMPLEXITY ===
        has_aggregation = len(agg_types) > 0
        has_multiple_tables = len(join_matches) > 0 or query_upper.count("FROM") > 1

        if has_multiple_tables and has_aggregation:
            patterns["complexity_distribution"]["complex"] += 1
        elif has_multiple_tables or has_aggregation:
            patterns["complexity_distribution"]["moderate"] += 1
        else:
            patterns["complexity_distribution"]["simple"] += 1

    # === CONVERT COUNTERS TO SORTED LISTS FOR READABILITY ===
    patterns["tables_used"] = dict(patterns["tables_used"].most_common())
    patterns["column_filters"] = dict(patterns["column_filters"].most_common(10))
    patterns["aggregations"] = dict(patterns["aggregations"].most_common())
    patterns["question_starters"] = dict(patterns["question_starters"].most_common(10))

    return patterns


# Prints results of pattern analysis in a human-readable format
def print_pattern_summary(patterns: Dict):
    """Print a human-readable summary of patterns"""
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"\n📊 Most Used Tables:")
    for table, count in list(patterns["tables_used"].items())[:5]:
        print(f"   {table}: {count} queries")

    print(f"\n🔍 Most Filtered Columns:")
    for col, count in list(patterns["column_filters"].items())[:5]:
        print(f"   {col}: {count} times")

    print(f"\n📈 Aggregation Types:")
    for agg, count in patterns["aggregations"].items():
        print(f"   {agg}: {count} queries")

    print(f"\n🔗 Join Queries: {len(patterns['join_patterns'])} multi-table queries")

    print(f"\n🤔 Question Starters:")
    for starter, count in list(patterns["question_starters"].items())[:5]:
        print(f"   '{starter}...': {count} questions")

    print(f"\n⚡ Complexity Distribution:")
    for level, count in patterns["complexity_distribution"].items():
        print(f"   {level.capitalize()}: {count} queries")

    print(f"\n🔄 Comparison Questions: {len(patterns['comparison_examples'])} found")

    print("=" * 60 + "\n")


def create_prompt_for_generation(
    examples: List[Dict[str, str]],
    schema: Dict[str, List[str]],
    patterns: Dict,
    batch_size: int = 10,
) -> str:
    """Create a prompt for the LLM to generate new examples"""

    # Sample a few examples
    sample_examples = random.sample(examples, min(5, len(examples)))

    prompt = f"""You are a SQL query generation expert for building standards and energy code databases.

DATABASE SCHEMA:
{json.dumps(schema, indent=2)}

PATTERN GUIDANCE (from existing queries):
- Common filtered columns: {', '.join(list(patterns['column_filters'].keys())[:5])}
- Aggregation types used: {', '.join(patterns['aggregations'].keys())}
- Complexity distribution: {patterns['complexity_distribution']['simple']} simple, {patterns['complexity_distribution']['moderate']} moderate, {patterns['complexity_distribution']['complex']} complex
- Common question starters: {', '.join([f'"{s}"' for s in list(patterns['question_starters'].keys())[:3]])}

EXAMPLE QUESTION-QUERY PAIRS:
"""

    for i, ex in enumerate(sample_examples, 1):
        prompt += f"\n{i}. Question: {ex['question']}\n"
        prompt += f"   SQL Query: {ex['query']}\n"

    prompt += f"""

TASK: Generate {batch_size} NEW question-query pairs that:
1. Use different combinations of tables and columns from the schema
2. Ask questions in varied ways (comparisons, aggregations, filtering, joins)
3. Cover different standards (ASHRAE 90.1, IECC) and versions
4. Include diverse climate zones, building types, and equipment types
5. Are realistic queries a building engineer or energy modeler would ask

REQUIREMENTS:
- Questions should be natural and specific
- SQL queries must be valid and use proper table/column names from the schema
- Don't overcomplicate queries with too many joins- prefer single table queries over complex joins
- Use LIKE operator for flexible matching (e.g., 'intended_surface_type LIKE "%Roof"' instead of exact matches)
- Use common, broad filter values that are likely to exist in the database
- Avoid overly specific combinations that might return no results
- Focus on practical, real-world questions that would return meaningful data
- Include a mix of simple filters, basic comparisons, and light analytical queries
- Prioritize queries that will return results over complex multi-table operations
- Favor providing up to 8 relevant columns in SELECT statements to provide valuable context
- If ordering is performed, remove NULL values from the results
- If using OR paired with an AND in WHERE clauses, use parentheses to clarify precedence
-- EXAMPLE: If checking walls in climate 7 or 8, use:
    WHERE (climate_zone_set LIKE '%7%' OR climate_zone_set LIKE '%8%') AND intended_surface_type LIKE '%Wall'

FLEXIBLE MATCHING EXAMPLES:
- Instead of: building_type = 'LargeOffice' → use: building_type LIKE '%Office%'
- Instead of: climate_zone = 'ASHRAE 169-2013-4A' → use: climate_zone LIKE '%4A%'
- Instead of: climate_zone_set = 'ClimateZone 4' → use: climate_zone_set LIKE '%4%'
- Instead of: intended_surface_type = 'ExteriorRoof' → use: intended_surface_type LIKE '%Roof%'

OUTPUT FORMAT (JSON):
{{
  "examples": [
    {{
      "question": "Your question here?",
      "query": "SELECT ... FROM ... WHERE ..."
    }}
  ]
}}

Generate {batch_size} examples now:"""

    return prompt


def generate_with_llm(prompt: str) -> List[Dict[str, str]]:
    """Call LLM to generate new examples using Ollama"""
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # Initialize Ollama LLM
    llm = ChatOllama(
        model="llama3.3:70b",
        temperature=0.7,  # Lower temperature for more consistent JSON
        base_url="http://rc-chat.pnl.gov:11434",
    )

    # Create chain
    prompt_template = PromptTemplate.from_template("{prompt}")
    llm_chain = prompt_template | llm | StrOutputParser()

    # Get response
    response_text = llm_chain.invoke({"prompt": prompt})

    # Parse JSON response
    try:
        # Extract JSON from response (handles markdown code blocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text

        data = json.loads(json_str.strip())
        return data.get("examples", [])
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Response was: {response_text[:500]}...")
        return []


def validate_queries_batch(
    examples: List[Dict[str, str]], db_path: str
) -> List[Dict[str, str]]:
    """Validate multiple queries in batch using a single database connection"""
    valid_examples = []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for i, ex in enumerate(examples):
            query = ex["query"]
            try:
                # First check syntax with EXPLAIN
                cursor.execute(f"EXPLAIN QUERY PLAN {query}")

                # Then actually execute to check if it returns data
                cursor.execute(query)
                results = cursor.fetchall()

                # Query is valid if it has syntax correctness AND returns at least one row
                has_results = len(results) > 0
                if has_results:
                    valid_examples.append(ex)
                else:
                    print(
                        f"  Query {i+1} returned no results: {ex['question'][:50]}..."
                    )

            except Exception as e:
                print(f"  Query {i+1} validation failed: {e}")
                print(f"    Question: {ex['question'][:50]}...")

        conn.close()

    except Exception as e:
        print(f"Database connection failed: {e}")
        return []

    return valid_examples


def generate_dataset(
    existing_csv: str, db_path: str, output_csv: str, target_count: int
):
    """Main function to generate expanded dataset"""

    print(f"Loading existing examples from {existing_csv}...")
    existing_example_dict = load_existing_examples(existing_csv)
    print(f"Loaded {len(existing_example_dict)} existing examples")

    print("Extracting database schema...")
    schema = get_database_schema(db_path)
    print(f"Found {len(schema)} tables")

    print("Analyzing patterns...")
    patterns = analyze_patterns(existing_example_dict)

    all_examples = existing_example_dict.copy()
    batches_needed = (target_count - len(existing_example_dict)) // 10 + 1

    print(
        f"\nGenerating {target_count - len(existing_example_dict)} new examples in {batches_needed} batches..."
    )

    for batch_num in range(batches_needed):
        print(f"\nBatch {batch_num + 1}/{batches_needed}...")

        prompt = create_prompt_for_generation(
            existing_example_dict, schema, patterns, batch_size=10
        )
        new_examples = generate_with_llm(prompt)

        # Validate examples in batch (much faster!)
        print(f"  Validating {len(new_examples)} generated examples...")
        valid_examples = validate_queries_batch(new_examples, db_path)

        # Add valid examples
        all_examples.extend(valid_examples)
        print(
            f"  Added {len(valid_examples)} valid examples ({len(valid_examples)}/{len(new_examples)} success rate)"
        )

        if len(all_examples) >= target_count:
            break

    # Save to CSV
    print(f"\nSaving {len(all_examples)} examples to {output_csv}...")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"])
        writer.writeheader()
        for ex in all_examples:
            writer.writerow({"question": ex["question"], "answer": ex["query"]})

    print(
        f"✓ Done! Generated {len(all_examples) - len(existing_example_dict)} new examples"
    )
    print(f"  Total examples: {len(all_examples)}")


if __name__ == "__main__":
    import os

    db_path = os.path.join("..", SQLITE_DB)
    existing_csv_path = os.path.join("dataset", "raw", EXISTING_CSV)
    output_csv_path = os.path.join("dataset", "raw", OUTPUT_CSV)

    # Generate dataset
    generate_dataset(
        existing_csv=existing_csv_path,
        db_path=db_path,
        output_csv=output_csv_path,
        target_count=TARGET_COUNT,
    )

    # Print pattern summary of the generated dataset
    print_pattern_summary(analyze_patterns(load_existing_examples(output_csv_path)))
