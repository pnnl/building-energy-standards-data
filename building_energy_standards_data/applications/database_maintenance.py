import sqlite3
import logging
import os

import building_energy_standards_data.database_tables as tables
from building_energy_standards_data.database_engine.assertions import assert_
from building_energy_standards_data.database_engine.database_util import (
    read_csv_to_list_dict,
    read_json_to_list_dict,
)

ROOT_DIR = os.path.dirname(__file__)


def create_openstudio_standards_database_from_csv(conn: sqlite3.Connection) -> None:
    """Create the OpenStudio Standards database from CSV files.

    Creates all database tables and populates them with data read from CSV files
    located in the data directory.

    Args:
        conn: SQLite database connection.
    """
    database_available_tables = tables.__gettables__()
    table_list = [table[1]() for table in database_available_tables]
    with conn:
        for datatable in table_list:
            datatable.create_a_table(conn)
            data = read_csv_to_list_dict(f"{datatable.initial_data_directory}.csv")

            datatable.add_records(conn, data)


def create_openstudio_standards_database_from_json(
    conn: sqlite3.Connection, path_suffix: str = ""
) -> None:
    """Create the OpenStudio Standards database from JSON files.

    Creates all database tables and populates them with data read from JSON files
    located in the data directory.

    Args:
        conn: SQLite database connection.
        path_suffix: Directory path suffix for the JSON files. Defaults to "".
    """
    database_available_tables = tables.__gettables__()
    table_list = [table[1]() for table in database_available_tables]
    with conn:
        for datatable in table_list:
            datatable.create_a_table(conn)
            data = read_json_to_list_dict(
                f"{path_suffix}{datatable.initial_data_directory}.json"
            )

            datatable.add_records(conn, data)


def create_database(conn: sqlite3.Connection) -> None:
    """Create the OpenStudio Standards database from JSON files.

    Convenience wrapper that calls create_openstudio_standards_database_from_json
    with the default data directory location.

    Args:
        conn: SQLite database connection.
    """
    create_openstudio_standards_database_from_json(
        conn, path_suffix=f"{ROOT_DIR}/../../"
    )


def export_openstudio_standards_database_to_csv(
    conn: sqlite3.Connection, save_dir: str = ""
) -> None:
    """Export the OpenStudio Standards database to CSV files.

    Exports all database tables to CSV files in the specified directory.

    Args:
        conn: SQLite database connection.
        save_dir: Directory where CSV files will be saved. Defaults to "".
    """
    database_available_tables = tables.__gettables__()
    table_list = [table[1]() for table in database_available_tables]
    with conn:
        for datatable in table_list:
            datatable.export_table_to_csv(conn, save_dir)


def export_openstudio_standards_database_to_json(
    conn: sqlite3.Connection, save_dir: str = ""
) -> None:
    """Export the OpenStudio Standards database to JSON files.

    Exports all database tables to JSON files in the specified directory.

    Args:
        conn: SQLite database connection.
        save_dir: Directory where JSON files will be saved. Defaults to "".
    """
    database_available_tables = tables.__gettables__()
    table_list = [table[1]() for table in database_available_tables]
    with conn:
        for datatable in table_list:
            datatable.export_table_to_json(conn, save_dir)
