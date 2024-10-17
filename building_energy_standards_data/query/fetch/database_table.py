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


def fetch_table(conn: sqlite3.Connection, table_name: str):
    """
    Fetch all data from a specific table
    :param conn:
    :param table_name: String data table
    :return: list of data or empty list
    """
    # Make sure the table exist
    if is_table_exist(conn, table_name):
        fetch_query = f"""SELECT * FROM {table_name}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_list_tuple_to_list_dict(cur.fetchall(), data_header)
    return []


def fetch_table_with_max_numbers_of_records(
    conn, table_name: str, max: int | None = None
):
    """
    Fetch data from a specific table limited to a max number of records
    :param conn:
    :param table_name: String data table
    :param max: max number of records to be returned
    :return: list of data or empty list
    """
    table = fetch_table(conn, table_name)
    if max and len(table) > max:
        table = table[0:max]
    return table


def fetch_columns_from_table(
    conn: sqlite3.Connection, table_name: str, field_names: list | str
):
    """
    Fetch specific columns from a specific table
    :param conn:
    :param table_name: String data table
    :param field_names: list of columns to fetch
    :return: list of data or empty list
    """
    # Make sure the table exist
    if is_field_in_table(conn, table_name, field_names):
        if isinstance(field_names, list):
            field_names = field_names.join(", ")
        fetch_query = f"""SELECT {field_names} FROM {table_name}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_list_tuple_to_list_dict(cur.fetchall(), data_header)
    return []


def fetch_column_from_table(conn: sqlite3.Connection, table_name: str, field_name: str):
    """
    Fetch specific column from a specific table
    :param conn:
    :param table_name: table name
    :param field_name: column to fetch
    :return: list of data in column
    """
    column_list = fetch_columns_from_table(conn, table_name, field_name)
    return [entry[field_name] for entry in column_list]


def fetch_a_record_from_table_by_id(
    conn: sqlite3.Connection, table_name: str, index: int
):
    """
    Fetch a data record matched by ID from a specific table
    :param conn:
    :param table_name: String lighting data table
    :param index: Integer, lighting object ID
    :return: dict
    """
    # Make sure the table exist
    if is_table_exist(conn, table_name):
        fetch_query = f"""SELECT * FROM {table_name} WHERE id={index}"""
        cur = conn.execute(fetch_query)
        data_header = list(map(lambda x: x[0], cur.description))

        return _convert_tuple_to_dict(cur.fetchone(), data_header)
    return dict()


def fetch_records_from_table_by_key_values(
    conn: sqlite3.Connection, table_name: str, key_value_dict: dict | None = None
):
    """
    Fetch a data record matched by key value pairs in the dict from a specific table
    :param conn:
    :param table_name: String data table
    :param key_value_dict: Dict, key value pair where Key shall be the column name and value shall be the value
    :return: dict
    """
    # Make sure the table exist
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


def fetch_table_names_containing_keyword(conn: sqlite3.Connection, keyword: str):
    """
    Fetch a data record matched by key value pairs in the dict from a specific table
    :param conn:
    :param keyword: keyword to search tables for
    :return: list
    """
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?"
    cur = conn.execute(query, ("%" + keyword + "%",))
    return _convert_list_single_tuple_to_list_str(cur.fetchall())
