import sqlite3
from typing import List


def _convert_list_tuple_to_list_dict(data: List[tuple], data_head_list: List[str]) -> List[dict]:
    """
    Convert a list of tuples to a list of dictionaries.

    Args:
        data: A list of tuples containing the data.
        data_head_list: A list of strings representing the keys for the dictionaries.

    Returns:
        A list of dictionaries mapping keys to values.
    """
    return [dict(zip(data_head_list, data_tuple)) for data_tuple in data]


def _convert_tuple_to_dict(data: tuple, data_head_list: List[str]) -> dict:
    """
    Convert a tuple to a dictionary.

    Args:
        data: The tuple of values.
        data_head_list: Keys to associate with the tuple values.

    Returns:
        A dictionary mapping keys to values.
    """
    return dict(zip(data_head_list, data))


def _convert_list_single_tuple_to_list_str(data: List[tuple]) -> List[str]:
    """
    Convert a list of single-element tuples to a list of strings.

    Args:
        data: A list of single-element tuples.

    Returns:
        A list of strings extracted from the tuples.
    """
    return [row[0] for row in data]


def is_index_in_table(
    conn: sqlite3.Connection, table_name: str | None, key: str | None, index: str | None
) -> bool:
    """
    Utility function to ensure the index exist in a table.

    Args:
        conn: sqlite3 connection
        table_name: string, a table's name
        key: string, the foreign key name
        index: integer, a table's index, primary key
    Returns:
        True if index is in table, False otherwise.
    """
    result = None
    # Make sure no value is None
    if all([table_name, key, index]):
        cursor = conn.cursor()
        if is_table_exist(conn, table_name):
            cursor.execute(f"SELECT id FROM {table_name} WHERE {key} = ?", (index,))
            result = cursor.fetchone()
    return True if result else False


def is_table_exist(conn: sqlite3.Connection, table_name) -> bool:
    """
    Utility function to ensure the table name provided is correct and exist in the openstudio_standards data tables

    Args:
        conn: sqlite3 connection
        table_name: string, a table's name

    Returns:
        True if table exists, False otherwise
    """
    cur = conn.cursor()
    list_of_tables = cur.execute(
        f"""SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name='{table_name}'"""
    ).fetchall()
    return True if list_of_tables else False


def is_field_in_table(
    conn: sqlite3.Connection, table_name, fields_to_check: list | str
) -> bool:
    """
    Utility function to ensure the table name provided is correct and exist in the openstudio_standards data tables

    Args:
        conn: sqlite3 connection
        table_name: string, a table's name
        fields_to_check: list or string, fields to check in the table

    Returns:
        True if all fields exist in the table, False otherwise
    """
    cur = conn.cursor()

    if not is_table_exist(conn, table_name):
        return False

    list_of_tables = cur.execute(f"""PRAGMA table_info({table_name})""").fetchall()

    if isinstance(fields_to_check, str):
        fields_to_check = [fields_to_check]

    if list_of_tables:
        existing_columns = [row[1] for row in list_of_tables]
        fields_exist = all(field in existing_columns for field in fields_to_check)
    else:
        fields_exist = False
    return fields_exist


def match_dict_data_by_key(primary_data: dict, secondary_data: dict) -> dict:
    """
    This function matches two data dictionaries (primary_data, secondary_data) and return only the matched portion of the dictionary
    Match only applies when only key is matched.

    If key matched, the value will use the one_data value

    Args:
        primary_data: The primary data dictionary.
        secondary_data: The secondary data dictionary.

    Returns:
        A dictionary containing only the keys that are present in both primary_data and secondary_data.
    """
    return {
        key: primary_data[key]
        for key in primary_data.keys()
        if key in secondary_data.keys()
    }
