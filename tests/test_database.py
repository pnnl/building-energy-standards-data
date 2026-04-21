import unittest, os, sqlite3, glob, shutil
from unittest import TestCase
from unittest import mock
import json
import tempfile
from pathlib import Path

from building_energy_standards_data.applications.database_maintenance import (
    create_openstudio_standards_database_from_csv,
    create_openstudio_standards_database_from_json,
    export_openstudio_standards_database_to_csv,
    export_openstudio_standards_database_to_json,
)
from building_energy_standards_data.database_engine.database import (
    DBOperation,
    copy_template_records_in_json_files,
)


CREATE_L3_TEST_TABLE = """
CREATE TABLE level_3_table (id INTEGER PRIMARY KEY, name TEXT);
"""
INSERT_L3_TEST_TABLE = f"""
    INSERT INTO level_3_table
    (name)
    VALUES (?);
"""

CREATE_L2_TABLE = """
CREATE TABLE level_2_table (id INTEGER PRIMARY KEY, associate_table TEXT, foreign_key TEXT)
"""

INSERT_L2_TABLE = f"""
    INSERT INTO level_2_table
    (associate_table, foreign_key)
    VALUES (?, ?);
"""


class SampleL3TestTable(DBOperation):
    def __init__(self):
        super(SampleL3TestTable, self).__init__(
            table_name="l3_table",
            record_template={},
            initial_data_directory="",
            create_table_query=CREATE_L3_TEST_TABLE,
            insert_record_query=INSERT_L3_TEST_TABLE,
        )

    def _preprocess_record(self, record):
        return (record["name"],)


class SampleL2TestTable(DBOperation):
    def __init__(self):
        super(SampleL2TestTable, self).__init__(
            table_name="test_table",
            record_template={},
            initial_data_directory="",
            create_table_query=CREATE_L2_TABLE,
            insert_record_query=INSERT_L2_TABLE,
        )

    def _preprocess_record(self, record):
        return (record["associate_table"], record["foreign_key"])

    def _get_weak_foreign_key_value(self, record):
        return record["associate_table"], "id", record["foreign_key"]


class TestWeakForeignKeyAssociation(unittest.TestCase):
    def setUp(self):
        # Create a test database with two tables and index
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        self.level_2_table = SampleL2TestTable()
        self.level_3_table = SampleL3TestTable()
        self.level_2_table.create_a_table(self.conn)
        self.level_3_table.create_a_table(self.conn)
        self.level_3_table.add_a_record(self.conn, {"name": "test_value_1"})  # index 1
        self.level_3_table.add_a_record(self.conn, {"name": "test_value_2"})  # index 2

    def tearDown(self):
        # close the database connection
        self.cur.close()
        self.conn.close()

    def test_index_exists(self):
        # Test that the function correctly identifies an existing index
        add_success = self.level_2_table.add_a_record(
            self.conn, {"associate_table": "level_3_table", "foreign_key": "1"}
        )
        self.assertTrue(add_success)

    def test_index_does_not_exist(self):
        # Test that the function validated the index is not exist
        add_success = self.level_2_table.add_a_record(
            self.conn, {"associate_table": "level_3_table", "foreign_key": "3"}
        )
        self.assertFalse(add_success)

    def test_table_does_not_exist(self):
        # Test if the table is not exist
        add_success = self.level_2_table.add_a_record(
            self.conn, {"associate_table": "missing_table", "foreign_key": "1"}
        )
        self.assertFalse(add_success)


def create_db(db_name, from_type=""):
    # Delete DB if already exists
    if os.path.isfile(f"{db_name}.db"):
        os.remove(f"{db_name}.db")
    conn = sqlite3.connect(f"{db_name}.db")
    # Create DB
    if from_type == "json":
        create_openstudio_standards_database_from_json(conn)
    else:
        create_openstudio_standards_database_from_csv(conn)
    return conn


def test_create_export_database():
    # Create DB from JSON file
    db_name = "openstudio_standards_data"
    conn = create_db(db_name=db_name, from_type="json")

    # Check that DB exists
    assert os.path.isfile(f"{db_name}.db")

    # Foreign key check
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_key_check;")
    res = cur.fetchall()
    assert len(res) == 0, f"Foreign key issue: {res}"

    # Create a copy of original JSON files
    if os.path.isdir("./original_database_files"):
        shutil.rmtree("./original_database_files", ignore_errors=True)
    shutil.copytree(
        "./building_energy_standards_data/database_files", "./original_database_files"
    )

    # Export data to JSON and CSV files
    export_openstudio_standards_database_to_json(
        conn, save_dir="./building_energy_standards_data/database_files/"
    )
    export_openstudio_standards_database_to_csv(
        conn, save_dir="./building_energy_standards_data/database_files/"
    )
    conn.close()

    # Regenerate DB from JSON and CSV files
    db_name = "openstudio_standards_data_from_csv"
    conn_csv = create_db(db_name=db_name, from_type="csv")
    db_name = "openstudio_standards_data_from_json"
    conn_json = create_db(db_name=db_name, from_type="json")

    # Export both DB to JSON files
    if not os.path.isdir("./tests/database_files_from_json"):
        os.mkdir("./tests/database_files_from_json")
    if not os.path.isdir("./tests/database_files_from_csv"):
        os.mkdir("./tests/database_files_from_csv")
    export_openstudio_standards_database_to_json(
        conn_json, save_dir="./tests/database_files_from_json/"
    )
    export_openstudio_standards_database_to_json(
        conn_csv, save_dir="./tests/database_files_from_csv/"
    )
    conn.close()

    # Compare original JSON files with the ones generated from both DB
    # There should be no difference between the JSON files originating
    # from a DB generated from JSON or CSV files
    filenames = glob.glob("./tests/database_files_from_json/*.json")
    filenames = [os.path.basename(f) for f in filenames]
    for f in filenames:
        with open(f"./tests/database_files_from_json/{f}") as f_from_json:
            data_from_json = json.load(f_from_json)
        with open(f"./tests/database_files_from_csv/{f}") as f_from_csv:
            data_from_csv = json.load(f_from_csv)
        with open(f"./original_database_files/{f}") as f_org:
            data_org = json.load(f_org)

        # Sort lists of dicts by converting to sorted tuples for comparison
        if isinstance(data_from_json, list):
            data_from_json_sorted = sorted(
                data_from_json, key=lambda x: json.dumps(x, sort_keys=True)
            )
            data_from_csv_sorted = sorted(
                data_from_csv, key=lambda x: json.dumps(x, sort_keys=True)
            )
            data_org_sorted = sorted(
                data_org, key=lambda x: json.dumps(x, sort_keys=True)
            )
        else:
            data_from_json_sorted = data_from_json
            data_from_csv_sorted = data_from_csv
            data_org_sorted = data_org

        assert (
            data_from_json_sorted == data_from_csv_sorted == data_org_sorted
        ), f"Content is different in {f} files"

    # Check for duplicate entries in the JSON files
    for f in filenames:
        with open(f"./tests/database_files_from_json/{f}") as json_file:
            data = json.load(json_file)

        if isinstance(data, list):
            # Convert records to tuples for duplicate detection (excluding 'id' field if present)
            records_as_tuples = []
            for record in data:
                # Create a sorted tuple of (key, value) pairs, excluding 'id'
                record_tuple = tuple(
                    sorted(
                        (k, str(v) if v is not None else None)
                        for k, v in record.items()
                        if k != "id"
                    )
                )
                records_as_tuples.append(record_tuple)

            # Check for duplicates
            unique_records = set(records_as_tuples)
            if len(unique_records) != len(records_as_tuples):
                duplicate_count = len(records_as_tuples) - len(unique_records)
                assert False, f"Found {duplicate_count} duplicate entries in {f}"

            unique_records = set(records_as_tuples)
            if len(unique_records) != len(records_as_tuples):
                duplicate_count = len(records_as_tuples) - len(unique_records)
                assert False, f"Found {duplicate_count} duplicate entries in {f}"


class TestCopyTemplateRecords(unittest.TestCase):
    """Test suite for copy_template_records_in_json_files function"""

    def setUp(self):
        """Create a temporary directory with test JSON files"""
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)

        # Create test JSON files with sample data
        self.test_file1_data = [
            {
                "template": "IECC-2024",
                "equipment_type": "PTAC",
                "cooling_type": "AirCooled",
                "minimum_capacity": 0,
                "maximum_capacity": 9999999999,
            },
            {
                "template": "IECC-2024",
                "equipment_type": "Air Conditioners",
                "cooling_type": "WaterCooled",
                "minimum_capacity": 65000,
                "maximum_capacity": 134999.99,
            },
            {
                "template": "90.1-2019",
                "equipment_type": "Chillers",
                "cooling_type": "AirCooled",
                "minimum_capacity": 100000,
                "maximum_capacity": 500000,
            },
        ]

        self.test_file2_data = [
            {
                "template": "IECC-2024",
                "building_type": "Office",
                "climate_zone": "1A",
                "u_factor": 0.5,
            },
            {
                "template": "IECC-2021",
                "building_type": "Retail",
                "climate_zone": "2A",
                "u_factor": 0.4,
            },
        ]

        # File without template field
        self.test_file3_data = [
            {
                "name": "Test",
                "value": 123,
            },
        ]

        # Write test files
        with open(self.test_dir_path / "hvac_test.json", "w") as f:
            json.dump(self.test_file1_data, f, indent=4)

        with open(self.test_dir_path / "envelope_test.json", "w") as f:
            json.dump(self.test_file2_data, f, indent=4)

        with open(self.test_dir_path / "other_test.json", "w") as f:
            json.dump(self.test_file3_data, f, indent=4)

    def tearDown(self):
        """Remove temporary directory and files"""
        shutil.rmtree(self.test_dir)

    def test_copy_template_basic(self):
        """Test basic template copying functionality"""
        summary = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # Check that 2 files were modified
        self.assertEqual(len(summary), 2)
        self.assertEqual(summary["hvac_test.json"], 2)
        self.assertEqual(summary["envelope_test.json"], 1)

        # Verify the actual file content
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            data = json.load(f)

        # Should have original 3 + 2 new records = 5 total
        self.assertEqual(len(data), 5)

        # Check that new records have correct template
        new_records = [r for r in data if r.get("template") == "IECC-2027"]
        self.assertEqual(len(new_records), 2)

        # Verify data integrity - new records should match original except template
        for new_record in new_records:
            self.assertEqual(new_record["template"], "IECC-2027")
            # Find matching original record
            matching_original = [
                r
                for r in self.test_file1_data
                if r.get("equipment_type") == new_record.get("equipment_type")
                and r.get("template") == "IECC-2024"
            ]
            self.assertEqual(len(matching_original), 1)
            # Compare all fields except template
            for key in new_record:
                if key != "template":
                    self.assertEqual(new_record[key], matching_original[0][key])

    def test_copy_template_dry_run(self):
        """Test that dry run mode doesn't modify files"""
        # Get original file content
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            original_data = json.load(f)

        summary = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=True,
        )

        # Summary should still be generated
        self.assertEqual(len(summary), 2)
        self.assertEqual(summary["hvac_test.json"], 2)

        # File should not be modified
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            data = json.load(f)

        self.assertEqual(data, original_data)
        self.assertEqual(len(data), 3)  # Should still have only 3 records

    def test_copy_template_no_matching_records(self):
        """Test behavior when no records match the source template"""
        summary = copy_template_records_in_json_files(
            source_template="NONEXISTENT-2099",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # Should return empty summary
        self.assertEqual(len(summary), 0)

    def test_copy_template_with_file_pattern(self):
        """Test filtering files with file_pattern parameter"""
        summary = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            file_pattern="hvac_*.json",
            dry_run=False,
        )

        # Should only process hvac_test.json
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary["hvac_test.json"], 2)

        # envelope_test.json should not be modified
        with open(self.test_dir_path / "envelope_test.json", "r") as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)  # Original count

    def test_copy_template_deep_copy(self):
        """Test that records are deep copied (no reference issues)"""
        summary = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # Read the file
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            data = json.load(f)

        # Modify a new record
        new_record = [r for r in data if r.get("template") == "IECC-2027"][0]
        new_record["equipment_type"] = "MODIFIED"

        # Check that original records are unchanged
        original_record = [
            r
            for r in data
            if r.get("template") == "IECC-2024"
            and r.get("minimum_capacity") == new_record.get("minimum_capacity")
        ][0]
        self.assertNotEqual(original_record["equipment_type"], "MODIFIED")

    def test_copy_template_invalid_directory(self):
        """Test that function raises error for invalid directory"""
        with self.assertRaises(FileNotFoundError):
            copy_template_records_in_json_files(
                source_template="IECC-2024",
                target_template="IECC-2027",
                database_files_dir="/nonexistent/path",
                dry_run=False,
            )

    def test_copy_template_preserves_existing_records(self):
        """Test that existing records are preserved"""
        # Get count of 90.1-2019 records before copy
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            original_data = json.load(f)
        original_901_count = len(
            [r for r in original_data if r.get("template") == "90.1-2019"]
        )

        summary = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # Verify 90.1-2019 records are still there
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            data = json.load(f)
        new_901_count = len([r for r in data if r.get("template") == "90.1-2019"])

        self.assertEqual(original_901_count, new_901_count)
        self.assertEqual(new_901_count, 1)

    def test_copy_template_multiple_calls(self):
        """Test that calling function multiple times does NOT create duplicates"""
        # First copy
        summary1 = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # Second copy (should NOT create duplicates due to duplicate prevention)
        summary2 = copy_template_records_in_json_files(
            source_template="IECC-2024",
            target_template="IECC-2027",
            database_files_dir=self.test_dir,
            dry_run=False,
        )

        # First call should copy records, second should copy nothing (duplicates prevented)
        self.assertEqual(summary1, {"hvac_test.json": 2, "envelope_test.json": 1})
        self.assertEqual(summary2, {})  # No records copied on second call

        # Verify file does NOT have duplicates
        with open(self.test_dir_path / "hvac_test.json", "r") as f:
            data = json.load(f)

        # Should have original 3 + 2 new = 5 total (NOT 7)
        self.assertEqual(len(data), 5)

        # Should have 2 IECC-2027 records (NOT 4)
        iecc_2027_records = [r for r in data if r.get("template") == "IECC-2027"]
        self.assertEqual(len(iecc_2027_records), 2)
