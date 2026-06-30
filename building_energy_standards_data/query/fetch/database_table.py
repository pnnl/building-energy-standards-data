"""
This module contains functions that help to fetch data from tables
"""

import sqlite3

from building_energy_standards_data.query.util import (
    _convert_list_tuple_to_list_dict,
    _convert_tuple_to_dict,
    _convert_list_single_tuple_to_list_str,
    is_table_exist,
    is_field_in_table,
)


def fetch_table(conn: sqlite3.Connection, table_name: str) -> list[dict]:
    """Fetch all data from a specific table.

    Args:
        conn: SQLite connection object.
        table_name: Name of the data table.

    Returns:
        List of dictionaries representing table records, or empty list if table doesn't exist.
    """
    # Verify the table exists before fetching
    if is_table_exist(conn, table_name):
        fetch_query = f"""SELECT * FROM {table_name}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_list_tuple_to_list_dict(cur.fetchall(), data_header)
    return []


def fetch_table_with_max_numbers_of_records(
    conn, table_name: str, max: int | None = None
) -> list[dict]:
    """Fetch data from a table limited to a maximum number of records.

    Args:
        conn: SQLite connection object.
        table_name: Name of the data table.
        max: Maximum number of records to return. If None, returns all records.

    Returns:
        List of dictionaries representing table records, or empty list if table doesn't exist.
    """
    table = fetch_table(conn, table_name)
    if max and len(table) > max:
        table = table[0:max]
    return table


def fetch_columns_from_table(
    conn: sqlite3.Connection, table_name: str, field_names: list | str
) -> list[dict]:
    """Fetch specific columns from a table.

    Args:
        conn: SQLite connection object.
        table_name: Name of the data table.
        field_names: List of column names or a single column name string to fetch.

    Returns:
        List of dictionaries with selected columns, or empty list if table/fields don't exist.
    """
    # Verify the table and fields exist before fetching
    if is_field_in_table(conn, table_name, field_names):
        if isinstance(field_names, list):
            field_names = ", ".join(field_names)
        fetch_query = f"""SELECT {field_names} FROM {table_name}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_list_tuple_to_list_dict(cur.fetchall(), data_header)
    return []


def fetch_column_from_table(conn: sqlite3.Connection, table_name: str, field_name: str) -> list:
    """Fetch a specific column from a table.

    Args:
        conn: SQLite connection object.
        table_name: Name of the table.
        field_name: Name of the column to fetch.

    Returns:
        List of values from the specified column.
    """
    column_list = fetch_columns_from_table(conn, table_name, field_name)
    return [entry[field_name] for entry in column_list]


def fetch_a_record_from_table_by_id(
    conn: sqlite3.Connection, table_name: str, index: int
) -> dict:
    """Fetch a single record from a table by ID.

    Args:
        conn: SQLite connection object.
        table_name: Name of the data table.
        index: Integer ID of the record to fetch.

    Returns:
        Dictionary representing the record, or empty dict if not found.
    """
    # Verify the table exists before fetching
    if is_table_exist(conn, table_name):
        fetch_query = f"""SELECT * FROM {table_name} WHERE id={index}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_tuple_to_dict(cur.fetchone(), data_header)
    return dict()


def fetch_records_from_table_by_key_values(
    conn: sqlite3.Connection, table_name: str, key_value_dict: dict | None = None
) -> list[dict]:
    """Fetch records from a table matching key-value pairs.

    Args:
        conn: SQLite connection object.
        table_name: Name of the data table.
        key_value_dict: Dictionary where keys are column names and values are filter values.
            If None, all records are returned.

    Returns:
        List of dictionaries representing matching records, or empty list if table doesn't exist.
    """
    # Verify the table exists before fetching
    if is_table_exist(conn, table_name):
        if not key_value_dict:
            return fetch_table(conn, table_name)

        conditions = []
        for key, value in key_value_dict.items():
            if value is None:
                conditions.append(f"{key} IS NULL")
            else:
                conditions.append(f"{key} = '{value}'")
        condition = " AND ".join(conditions)
        fetch_query = f"""SELECT * FROM  {table_name} WHERE {condition}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))
        return _convert_list_tuple_to_list_dict(cur.fetchall(), data_header)
    return []


def fetch_table_names_containing_keyword(conn: sqlite3.Connection, keyword: str) -> list[str]:
    """Fetch table names containing a keyword.

    Args:
        conn: SQLite connection object.
        keyword: Keyword to search for in table names.

    Returns:
        List of table names matching the keyword.
    """
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?"
    cur = conn.execute(query, ("%" + keyword + "%",))
    return _convert_list_single_tuple_to_list_str(cur.fetchall())
