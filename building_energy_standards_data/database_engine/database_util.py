from typing import Any

import csv
import json


def read_csv_to_tuples(csv_dir: str) -> list[tuple]:
    """Read a CSV file and convert each row to a tuple.

    Args:
        csv_dir: Path to the CSV file.

    Returns:
        List of tuples, one per row, with empty strings converted to None.

    Raises:
        ValueError: If the file cannot be decoded with any of the attempted encodings.
    """
    # Try UTF-8 first, then fall back to latin-1 if that fails
    encodings_to_try = ["utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings_to_try:
        try:
            table_list = []
            with open(csv_dir, mode="r", encoding="utf-8-sig") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                for row in csv_reader:
                    # Convert empty strings to None for consistent null representation
                    new_row = [cell if cell else None for cell in row]
                    table_list.append(tuple(new_row))
            return table_list
        except UnicodeDecodeError:
            continue

    # If all encodings fail, raise an error
    raise ValueError(
        f"Could not decode file {csv_dir} with any of the attempted encodings: "
        f"{', '.join(encodings_to_try)}"
    )


def read_csv_to_list_dict(csv_dir: str) -> list[dict]:
    """Read a CSV file and convert to a list of dictionaries.

    Args:
        csv_dir: Path to the CSV file.

    Returns:
        List of dictionaries, one per row, excluding id fields.

    Raises:
        ValueError: If the file cannot be decoded with any of the attempted encodings.
    """
    # Try UTF-8 first, then fall back to latin-1 if that fails
    encodings_to_try = ["utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings_to_try:
        try:
            with open(csv_dir, mode="r", encoding=encoding) as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=",")
                table_list = [
                    {key: row[key] for key in row if key != "id"} for row in csv_reader
                ]
            return table_list
        except UnicodeDecodeError:
            continue

    # If all encodings fail, raise an error
    raise ValueError(
        f"Could not decode file {csv_dir} with any of the attempted encodings: "
        f"{', '.join(encodings_to_try)}"
    )


def read_json_to_list_dict(json_dir: str) -> list[dict]:
    """Read a JSON file and convert to a list of dictionaries.

    Args:
        json_dir: Path to the JSON file.

    Returns:
        List of dictionaries from the JSON file, excluding id fields.
    """
    with open(json_dir, mode="r") as json_file:
        json_table = json.loads(json_file.read())
        table_list = [
            {key: record[key] for key in record if key != "id"} for record in json_table
        ]
    return table_list


def is_float(element: Any) -> bool:
    """Verify if an element is a float data type.

    Args:
        element: The element to test.

    Returns:
        True if the element can be converted to float, False otherwise.
    """
    if element is None:
        return False
    try:
        float(element)
    except ValueError:
        return False
    return True


def getattr_either(key: str, record: dict, option: Any = None) -> str | None:
    """Retrieve a value from a dictionary with a default fallback option.

    A helper function to retrieve a key from a record dictionary with an optional
    default value returned when the key is missing or empty.

    Args:
        key: The dictionary key to retrieve.
        record: Dictionary that may contain a value for the key.
        option: Default value returned when key is missing or empty. Defaults to None.

    Returns:
        The value associated with the key as a string, or the option value if the
        key is missing or empty.
    """
    if record.get(key) == "":  # Used for reading data from CSV
        return option
    elif record.get(key) is None:  # Used for reading data from CSV
        return option
    else:
        return f"{record[key]}"
