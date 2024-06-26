import sqlite3

from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
lighting_zone: NUMERIC
allowance_type: TEXT
allowance: NUMERIC
allowance_unit: TEXT
tradable: TEXT
off_control: TEXT
daylight_off_control: TEXT
scheduled_off_control: TEXT
scheduled_light_reduction_control: TEXT
occupancy_sensing_light_reduction_control: TEXT
annotation: TEXT (optional)
"""

CREATE_EXT_LIGHT_DEF_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY,
template TEXT NOT NULL,
lighting_zone NUMERIC,
allowance_type TEXT NOT NULL,
allowance NUMERIC,
allowance_unit TEXT NOT NULL,
tradable TEXT NOT NULL,
off_control TEXT,
daylight_off_control TEXT,
scheduled_off_control TEXT,
scheduled_light_reduction_control TEXT,
occupancy_sensing_light_reduction_control TEXT,
annotation TEXT);
"""

INSERT_A_LIGHT_RECORD = """
    INSERT INTO %s (
template,
lighting_zone,
allowance_type,
allowance,
allowance_unit,
tradable,
off_control,
daylight_off_control,
scheduled_off_control,
scheduled_light_reduction_control,
occupancy_sensing_light_reduction_control,
annotation
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "lighting_zone": "",
    "allowance_type": "",
    "allowance": 0.0,
    "allowance_unit": "W/ft2",
    "tradable": "FALSE",
    "off_control": "",
    "daylight_off_control": "",
    "scheduled_off_control": "",
    "scheduled_light_reduction_control": "",
    "occupancy_sensing_light_reduction_control": "",
    "annotation": "",
}


class ExtLightDef(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(ExtLightDef, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_EXT_LIGHT_DEF_TABLE % table_name,
            insert_record_query=INSERT_A_LIGHT_RECORD % table_name,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "template",
            "allowance_type",
            "allowance_unit",
            "tradable",
            "off_control",
            "daylight_off_control",
            "scheduled_off_control",
            "scheduled_light_reduction_control",
            "occupancy_sensing_light_reduction_control",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = ["lighting_zone", "allowance"]

        for f in float_expected:
            if record.get(f):
                assert is_float(
                    record.get(f)
                ), f"{f} requires to be numeric data type, instead got {record[f]}"
        return True

    def _preprocess_record(self, record):
        """

        :param record: dictionary
        :return:
        """
        record_tuple = (
            getattr_either("template", record),
            getattr_either("lighting_zone", record),
            getattr_either("allowance_type", record),
            getattr_either("allowance", record),
            getattr_either("allowance_unit", record),
            getattr_either("tradable", record),
            getattr_either("off_control", record),
            getattr_either("daylight_off_control", record),
            getattr_either("scheduled_off_control", record),
            getattr_either("scheduled_light_reduction_control", record),
            getattr_either("occupancy_sensing_light_reduction_control", record),
            getattr_either("annotation", record),
        )
        return record_tuple
