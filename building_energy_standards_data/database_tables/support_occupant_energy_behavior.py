from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_occupant_energy_behavior"

RECORD_HELP = """
Must provide a dict that contains the following key-value pairs:
energy_behavior_name TEXT NOT NULL UNIQUE ,
cooling_setpoint NUMERIC,
cooling_setpoint_units TEXT NOT NULL,
heating_setpoint NUMERIC,
heating_setpoint_units TEXT NOT NULL,
minimum_dimming_level NUMERIC,
annotation TEXT
"""

CREATE_ENERGY_BEHAVIOR_TABLE = """
CREATE TABLE IF NOT EXISTS support_occupant_energy_behavior (
    energy_behavior_name TEXT UNIQUE NOT NULL PRIMARY KEY,
    cooling_setpoint NUMERIC,
    cooling_setpoint_units TEXT NOT NULL,
    heating_setpoint NUMERIC,
    heating_setpoint_units TEXT NOT NULL,
    minimum_dimming_level NUMERIC,
    annotation TEXT
);
"""

INSERT_ENERGY_BEHAVIOR = """
    INSERT INTO support_occupant_energy_behavior
    (energy_behavior_name, 
     cooling_setpoint, 
     cooling_setpoint_units,
     heating_setpoint, 
     heating_setpoint_units,
     minimum_dimming_level,annotation)
    VALUES (?, ?, ?, ?, ?, ?,?);
"""

RECORD_TEMPLATE = {
    "energy_behavior_name": "",
    "cooling_setpoint": 0.0,
    "cooling_setpoint_units": "",
    "heating_setpoint": 0.0,
    "heating_setpoint_units": "",
    "minimum_dimming_level": 0.0,
    "annotation": "",
}


class SupportEnergyBehaviorTable(DBOperation):
    def __init__(self):
        super(SupportEnergyBehaviorTable, self).__init__(
            table_name="support_occupant_energy_behavior",
            record_template=RECORD_TEMPLATE,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
            create_table_query=CREATE_ENERGY_BEHAVIOR_TABLE,
            insert_record_query=INSERT_ENERGY_BEHAVIOR,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "energy_behavior_name",
            "cooling_setpoint_units",
            "heating_setpoint_units",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "cooling_setpoint",
            "heating_setpoint",
            "minimum_dimming_level",
        ]

        for f in float_expected:
            if record.get(f):
                assert is_float(
                    record.get(f)
                ), f"{f} requires to be numeric data type, instead got {record[f]}"
        return True

    def _preprocess_record(self, record):
        """

        :param record: dict
        :return:
        """

        return (
            getattr_either("energy_behavior_name", record),
            getattr_either("cooling_setpoint", record),
            getattr_either("cooling_setpoint_units", record),
            getattr_either("heating_setpoint", record),
            getattr_either("heating_setpoint_units", record),
            getattr_either("minimum_dimming_level", record),
            getattr_either("annotation", record),
        )
