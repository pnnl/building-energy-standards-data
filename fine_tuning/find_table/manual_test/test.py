import json
import csv
from pathlib import Path
import re

from fine_tuning.find_table.lookup_pipeline import TABLE_NAMES, QueryPipeline

query_pipeline = QueryPipeline()


def save_table_descriptors_to_json():
    table_names = query_pipeline.schema_service.get_table_names(table_filter=TABLE_NAMES)
    table_descriptors = {
        table_name: query_pipeline.schema_service.parse_table_name(table_name).__dict__
        for table_name in table_names
    }

    with open(
        "fine_tuning/find_table/manual_test/output/table_descriptors.json", "w"
    ) as f:
        json.dump(table_descriptors, f, indent=2)


def compare_descriptor_from_queries():
    golden_dataset_path = Path("fine_tuning/dataset/raw/manual_std_queries.csv")
    output_path = Path("fine_tuning/find_table/manual_test/output/results.json")

    extract_table_pattern = re.compile(
        r"(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)", re.IGNORECASE
    )

    with open(golden_dataset_path, newline="", encoding="latin-1") as f:
        reader = csv.DictReader(f)

        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write("[\n")

            first = True
            for row in reader:
                expected_tables = extract_table_pattern.findall(row["answer"])

                query_attrs = query_pipeline.extract_descriptor_attributes(
                    row["question"]
                )
                table_metadata = query_pipeline.schema_service.generate_all_metadata(
                    include_columns=False, include_descriptor=True, table_filter = TABLE_NAMES
                )
                ranked_results = query_pipeline.rank_tables(query_attrs, table_metadata)

                result_entry = {
                    "question": row["question"],
                    "expected": [
                        {
                            "table": table_name,
                            "descriptor": query_pipeline.schema_service.parse_table_name(
                                table_name
                            ).__dict__,
                        }
                        for table_name in expected_tables
                    ],
                    "predicted_descriptor": query_attrs,
                    "closest_matches": [
                        {"table": table, "score": score}
                        for table, score in ranked_results
                    ],
                }

                if not first:
                    out_f.write(",\n")
                else:
                    first = False

                json.dump(result_entry, out_f, indent=2)

                out_f.flush()

            out_f.write("\n]")

def calculate():
    output_path = Path("fine_tuning/find_table/manual_test/output/results.json")
    with open(output_path, "r", encoding="utf-8") as out_f:
        data = json.load(out_f)
    data = [v for v in data if v["expected"][0]["table"] in TABLE_NAMES]

    matches_count = 0

    for item in data:
        expected_tables = {e["table"] for e in item["expected"]}
        closest_tables = {c["table"] for c in item["closest_matches"]}

        if expected_tables & closest_tables:  # intersection non-empty
            matches_count += 1
        else:
            print(expected_tables, closest_tables)

    percentage = (matches_count / len(data)) * 100
    print(f"Expected table appears in closest matches: {percentage:.2f}% of cases")


if __name__ == "__main__":
    # save_table_descriptors_to_json()
    # compare_descriptor_from_queries()
    calculate()

