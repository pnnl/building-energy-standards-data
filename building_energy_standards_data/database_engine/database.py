from typing import Optional

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


def create_connect(db_file: str | None) -> sqlite3.Connection | None:
    """Create a connection to the SQLite database.

    Args:
        db_file: Path to the database file. If None, uses the default DB_FILE.

    Returns:
        SQLite connection object, or None if connection fails.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file if db_file else DB_FILE)
        # Enable foreign keys execution
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        logging.error(e)
    return conn


def copy_template_records_in_json_files(
    source_template: str,
    target_template: str,
    database_files_dir: Optional[str] = None,
    file_pattern: str = "*.json",
    dry_run: bool = False,
) -> dict[str, int]:
    """Copy all records from a source template to a target template in JSON files.

    Reads all JSON files in the database_files directory, finds records matching the
    source template, creates copies with the target template name, and writes the
    updated data back to the files.

    Args:
        source_template: Template name to copy from (e.g., "IECC-2024").
        target_template: New template name to create (e.g., "IECC-2027").
        database_files_dir: Path to the database_files directory. If None, uses the
            default relative path. Defaults to None.
        file_pattern: File pattern to match. Defaults to "*.json".
        dry_run: If True, only prints what would be done without modifying files.
            Defaults to False.

    Returns:
        Dictionary mapping filenames to number of records copied.

    Raises:
        FileNotFoundError: If the database files directory cannot be found.
    """
    # Determine the database_files directory
    if database_files_dir is None:
        # Default to the database_files directory relative to this file
        current_dir = Path(__file__).parent.parent
        db_dir = current_dir / "database_files"
    else:
        db_dir = Path(database_files_dir)

    if not db_dir.exists():
        raise FileNotFoundError(
            f"Database files directory not found: {db_dir}"
        )

    # Get all JSON files in the directory
    json_files = list(db_dir.glob(file_pattern))

    if not json_files:
        logging.warning(f"No JSON files found in {db_dir}")
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
        table_name: str,
        record_template: dict,
        initial_data_directory: str,
        create_table_query: str,
        insert_record_query: str,
    ) -> None:
        """Initialize a DBOperation instance.

        Args:
            table_name: Name of the database table.
            record_template: Dictionary template for table records.
            initial_data_directory: Path to the initial data directory.
            create_table_query: SQL query to create the table.
            insert_record_query: SQL query to insert a record.
        """
        self.data_table_name = table_name
        self.record_template = record_template
        self.initial_data_directory = initial_data_directory
        self.create_table_query = create_table_query
        self.insert_record_query = insert_record_query

    def create_a_table(self, connection: sqlite3.Connection) -> bool:
        """Create a table in the database.

        Args:
            connection: SQLite database connection.

        Returns:
            True if table creation succeeded.
        """
        logging.info(f"creating table: {self.data_table_name}")
        connection.execute(self.create_table_query)
        return True

    def add_a_record(self, connection: sqlite3.Connection, record: dict) -> bool:
        """Add a single record to the table.

        Args:
            connection: SQLite database connection.
            record: Dictionary containing the record data.

        Returns:
            True if the record was successfully added, False otherwise.
        """
        # Run data validation, raise exception if data is not validated.
        cur = connection.cursor()
        success_added = False
        if self.validate_record_datatype(record) and self.validate_weak_foreign_key(
            connection, record
        ):
            cur.execute(self.insert_record_query, self._preprocess_record(record))
            connection.commit()
            success_added = True
        return success_added

    def add_records(self, connection: sqlite3.Connection, records: list[dict]) -> bool:
        """Add multiple records to the table.

        Args:
            connection: SQLite database connection.
            records: List of dictionaries containing record data.

        Returns:
            True if all records were successfully added, False otherwise.
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

    def get_all_records(self, connection: sqlite3.Connection) -> list:
        """Retrieve all records from the table.

        Args:
            connection: SQLite database connection.

        Returns:
            List of all records in the table.
        """
        return connection.execute(self._get_retrieve_all_query()).fetchall()

    def get_record_info(self) -> None:
        """Return the record info of the table.

        Returns:
            None
        """
        pass

    def get_record_template(self) -> dict:
        """Get a record template for the table.

        Returns:
            Dictionary containing the record template.
        """
        return self.record_template

    def validate_record_datatype(self, record: dict) -> bool:
        """Validate the data types in a record.

        This function is used to set special data requirements that the SQLite schema
        cannot verify (e.g., a value must be an int).

        Args:
            record: Dictionary containing a map of column to value in a row.

        Returns:
            True if all data types are valid, False otherwise.
        """
        return True

    def validate_weak_foreign_key(self, conn: sqlite3.Connection, record: dict) -> bool:
        """Validate weak foreign key references in a record.

        Validates if a key exists in a weakly associated table. In OSSTD, a weak
        associated table is one where the primary key is referenced by another table
        in a column instead of a SQL foreign key relationship. For example, the
        level_2_lighting_space_type table contains level_3_lighting_definition_id that
        references an index from the table specified in the level_3_lighting_definition_table
        column. For weak foreign keys, this function determines whether the addition
        or update is valid.

        Args:
            conn: SQLite connection object.
            record: Dictionary containing the record data.

        Returns:
            True if the weak foreign key reference is valid, False otherwise.
        """
        associate_table, key, value = self._get_weak_foreign_key_value(record)
        # Any falsy value (no association) should return True, or pass the is_index_in_table check.
        return not all([associate_table, key, value]) or is_index_in_table(
            conn, associate_table, key, value
        )

    def export_table_to_csv(self, conn: sqlite3.Connection, save_dir: str = "") -> None:
        """Export the table to a CSV file.

        Args:
            conn: SQLite connection object.
            save_dir: Path where the CSV file will be saved. Defaults to "".
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

    def export_table_to_json(self, conn: sqlite3.Connection, save_dir: str = "") -> None:
        """Export the table to a JSON file.

        Args:
            conn: SQLite connection object.
            save_dir: Path where the JSON file will be saved. Defaults to "".
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
    def _get_weak_foreign_key_value(self, record: dict) -> tuple[str | None, str | None, str | None]:
        """Extract weak foreign key values from a record.

        Function to extract values from a record for weak foreign key validation.
        Override this method in subclasses to provide specific validation logic.

        Args:
            record: Dictionary containing the record data.

        Returns:
            Tuple of (associate_table, key, value). All values default to None
            if no weak foreign key is defined.
        """
        return None, None, None

    def _preprocess_record(self, record: dict) -> dict:
        """Preprocess a record before insertion into the table.

        Override this method in subclasses to perform custom record transformations.

        Args:
            record: Dictionary containing the record data.

        Returns:
            The preprocessed record dictionary.
        """
        return record

    def _get_retrieve_all_query(self) -> str:
        """Get the SQL query to retrieve all records from the table.

        Returns:
            SQL SELECT query string.
        """
        return f"SELECT * FROM {self.data_table_name}"
