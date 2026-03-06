import sqlite3
from sqlite3 import Error
import csv
import json
import logging
import os
from pathlib import Path
from copy import deepcopy

from building_energy_standards_data.database_engine.assertions import assert_
from building_energy_standards_data.query.util import is_index_in_table

DB_FILE = "openstudio_standards_database.db"


def create_connect(db_file):
    """
    create a database_tables connection to the SQLite database_tables specified by db_file
    :param db_file: database_tables file or None (None uses default
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file if db_file else DB_FILE)
        # enable foreign keys execution
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        logging.error(e)
    return conn


def copy_template_records_in_json_files(
    source_template: str,
    target_template: str,
    database_files_dir: str = None,
    file_pattern: str = "*.json",
    dry_run: bool = False,
):
    """
    Copy all records from a source template to a new target template in JSON files.
    This function reads all JSON files in the database_files directory, finds records
    matching the source template, creates copies with the target template name, and
    writes the updated data back to the files.

    :param source_template: str - The template name to copy from (e.g., "IECC-2024")
    :param target_template: str - The new template name to create (e.g., "IECC-2027")
    :param database_files_dir: str - Path to the database_files directory. If None, uses the default relative path
    :param file_pattern: str - File pattern to match (default: "*.json")
    :param dry_run: bool - If True, only prints what would be done without modifying files
    :return: dict - Summary of operations performed {filename: number_of_records_copied}
    """
    # Determine the database_files directory
    if database_files_dir is None:
        # Default to the database_files directory relative to this file
        current_dir = Path(__file__).parent.parent
        database_files_dir = current_dir / "database_files"
    else:
        database_files_dir = Path(database_files_dir)

    if not database_files_dir.exists():
        raise FileNotFoundError(
            f"Database files directory not found: {database_files_dir}"
        )

    # Get all JSON files in the directory
    json_files = list(database_files_dir.glob(file_pattern))

    if not json_files:
        logging.warning(f"No JSON files found in {database_files_dir}")
        return {}

    summary = {}
    total_records_copied = 0

    logging.info(
        f"Copying records from template '{source_template}' to '{target_template}'"
    )
    logging.info(f"Found {len(json_files)} JSON files to process")

    for json_file in json_files:
        try:
            # Read the JSON file
            with open(json_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logging.warning(f"Skipping {json_file.name}: Not a list of records")
                continue

            # Find records matching the source template
            matching_records = [
                record for record in data if record.get("template") == source_template
            ]

            if not matching_records:
                logging.debug(
                    f"No records found in {json_file.name} with template '{source_template}'"
                )
                continue

            # Create copies with the new template name
            new_records = []
            for record in matching_records:
                new_record = deepcopy(record)
                new_record["template"] = target_template
                new_records.append(new_record)

            records_copied = len(new_records)
            summary[json_file.name] = records_copied
            total_records_copied += records_copied

            if dry_run:
                logging.info(
                    f"[DRY RUN] Would add {records_copied} records to {json_file.name}"
                )
            else:
                # Add new records to the data
                data.extend(new_records)

                # Write back to the file
                with open(json_file, "w") as f:
                    json.dump(data, f, indent=4)

                logging.info(f"Added {records_copied} records to {json_file.name}")

        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON in {json_file.name}: {e}")
        except Exception as e:
            logging.error(f"Error processing {json_file.name}: {e}")

    # Print summary
    if summary:
        logging.info(
            f"\nSummary: Copied {total_records_copied} total records across {len(summary)} files"
        )
        if dry_run:
            logging.info("[DRY RUN] No files were modified")
    else:
        logging.info(f"No records found with template '{source_template}' in any files")

    return summary


class DBOperation:
    def __init__(
        self,
        table_name,
        record_template,
        initial_data_directory,
        create_table_query,
        insert_record_query,
    ):
        """
        DB Operation class
        :param table_name: String name of the table
        :param record_template: dictionary record template
        :param initial_data_directory: String initial data directory
        :param create_table_query: String create table query
        :param insert_record_query: String insert record query
        """
        self.data_table_name = table_name
        self.record_template = record_template
        self.initial_data_directory = initial_data_directory
        self.create_table_query = create_table_query
        self.insert_record_query = insert_record_query

    def create_a_table(self, connection):
        """
        Create a table - no return
        :param connection:
        :return:
        """
        logging.info(f"creating table: {self.data_table_name}")
        connection.execute(self.create_table_query)
        return True

    def add_a_record(self, connection, record: dict):
        """
        Add a record to a table
        :param connection:
        :param record: dict contains the dictionary of record
        :return: the index of the newly inserted record.
        """
        # run data validation, raise exception if data is not validated.
        cur = connection.cursor()
        success_added = False
        if self.validate_record_datatype(record) and self.validate_weak_foreign_key(
            connection, record
        ):
            cur.execute(self.insert_record_query, self._preprocess_record(record))
            connection.commit()
            success_added = True
        return success_added

    def add_records(self, connection, records: list[dict]) -> bool:
        """
        Add records to a table
        :param connection:
        :param records: list of table records
        :return: bool indicating success or failure
        """
        cur = connection.cursor()

        valid_records = []
        for record in records:
            logging.info(record)
            assert_(
                self.validate_record_datatype(record)
                and self.validate_weak_foreign_key(connection, record),
                f"Unsuccessful adding a new record: {record} to table {self.data_table_name}",
            )
            valid_records.append(self._preprocess_record(record))

        if valid_records:
            cur.executemany(self.insert_record_query, valid_records)
            connection.commit()
            return True

        return False

    def get_all_records(self, connection):
        """
        Retrieve all data records
        :param connection:
        :return:
        """
        return connection.execute(self._get_retrieve_all_query()).fetchall()

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        pass

    def get_record_template(self):
        """
        Get a record template of a table
        :return:
        """
        return self.record_template

    def validate_record_datatype(self, record):
        """
        Validate the data. This function shall be used to set special data requirement that SQLite schema cannot
        verify. e.g., a data's data type shall be int.

        :param record: dict
        A dictionary that contains a map column to value in a row.
        :return: boolean
        """
        return True

    def validate_weak_foreign_key(self, conn, record):
        """
        Validate if a key is existing in a weak associated table. The definition of weak associate table in OSSTD
        means when the primary key in a table is referenced by another table in a column instead of SQL foreign key
        relationship. An example is the level_2_lighting_space_type contains level_3_lighting_definition_id that
        references an index from the table specified in the column level_3_lighting_definition_table.
        For weak foreign key, we will use this function to determine whether it is correct addition or update.

        :param: conn, SQL3lite connection
        :param: record: dictionary
        """
        associate_table, key, value = self._get_weak_foreign_key_value(record)
        # any value is Falsy (no association) should return True, or pass the is_index_in_table check.
        return not all([associate_table, key, value]) or is_index_in_table(
            conn, associate_table, key, value
        )

    def export_table_to_csv(self, conn, save_dir=""):
        """
        A function that exports the table into a .csv file

        :param conn: SQLite3Connection object
        :param save_dir: str, path that saves the csv file
        :return:
        """
        cursor = conn.cursor()
        cursor.execute(self._get_retrieve_all_query())
        csv_dir = f"{save_dir}{self.data_table_name}.csv"
        with open(csv_dir, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow([i[0] for i in cursor.description if i[0] != "id"])
            rows = []
            # Exclude IDs
            exclude_first_row = True if cursor.description[0][0] == "id" else False
            rows = [i[1:] for i in cursor] if exclude_first_row else cursor
            csv_writer.writerows(rows)

    def export_table_to_json(self, conn, save_dir=""):
        """
        A function that exports the table into a .json file

        :param conn: SQLite3Connection object
        :param save_dir: str, path that saves the json file
        :return:
        """
        cursor = conn.cursor()
        cursor.execute(self._get_retrieve_all_query())
        r = [
            dict((cursor.description[i][0], value) for i, value in enumerate(row))
            for row in cursor.fetchall()
        ]
        # Exclude IDs
        for i in r:
            if "id" in i.keys():
                del i["id"]
        json_dir = f"{save_dir}{self.data_table_name}.json"
        json_output = json.dumps(r, indent=4)
        with open(json_dir, "w", newline="\r\n") as json_file:
            json_file.write(json_output)

    # Functions to be overridden based on need
    def _get_weak_foreign_key_value(self, record):
        """
        Function to extract values from a record for weak foreign key validation
        :param record: dictionary
        :return
        associate_table: str - table that has weak foreign cooneciton
        key: the foreign key
        value: the foreign key value
        default are NONE (falsy)
        """
        return None, None, None

    def _preprocess_record(self, record):
        """
        Function that pre-process a record before insert to Table.

        :param record:
        :return:
        """
        return record

    def _get_retrieve_all_query(self):
        """
        Function to retrieve all records in a table
        :return:
        """
        return f"SELECT * FROM {self.data_table_name}"
