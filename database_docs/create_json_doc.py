import json
import os

from database_engine.database import create_connect
from query.fetch.database_table import (
    fetch_table,
    fetch_table_names_containing_keyword,
)


def create_json_doc():
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # create connection to database
    database_path = f"{current_directory}/../openstudio_standards_data.db"
    conn = create_connect(database_path)

    # fetch all table names
    table_names = fetch_table_names_containing_keyword(conn, "")

    # get list of fields to not include in doc_base
    fields_to_ignore_path = f"{current_directory}/fields_to_ignore.txt"
    ignore_fields = []
    if os.path.exists(fields_to_ignore_path):
        with open(fields_to_ignore_path, "r") as ignore_file:
            ignore_fields = [line.strip() for line in ignore_file]

    # fetch all field names
    field_names = set()
    for table_name in table_names:
        first_row = fetch_table(conn, table_name)[0]
        for field in first_row.keys():
            if field not in ignore_fields:
                field_names.add(field)

    field_names, table_names = sorted(field_names), sorted(table_names)

    # write descriptions to a dictionary
    doc_base_path = f"{current_directory}/doc_base.json"
    if os.path.exists(doc_base_path) and os.path.getsize(doc_base_path) > 0:
        # don't overwrite preexisting descriptions
        with open(doc_base_path, "r") as json_file:
            json_data = json.load(json_file)

        field_descriptions_dict, table_descriptions_dict = {}, {}
        assert list(json_data.keys()) == ["field descriptions", "table descriptions"]
        for key in field_names:
            description = json_data["field descriptions"].get(key)
            if not description:
                description = "todo"
            field_descriptions_dict[key] = description

        for key in table_names:
            description = json_data["table descriptions"].get(key)
            if not description:
                description = "todo"
            table_descriptions_dict[key] = description
    else:
        field_descriptions_dict, table_descriptions_dict = {
            key: "todo" for key in field_names
        }, {key: "todo" for key in table_names}

    doc_dict = {
        "field descriptions": field_descriptions_dict,
        "table descriptions": table_descriptions_dict,
    }

    json_file_path = f"{current_directory}/doc_base.json"
    with open(json_file_path, "w") as f:
        json.dump(doc_dict, f, indent=2)

    print(f"JSON doc has been created at {json_file_path}")


if __name__ == "__main__":
    create_json_doc()
