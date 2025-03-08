from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
air_system: TEXT
air_system_component: TEXT
fan_system: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
fan_power_allowance: NUMERIC
annotation: TEXT
"""

CREATE_SYSTEM_requirements_FAN_POWER_ALLOWANCE_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
air_system TEXT NOT NULL,
air_system_component TEXT NOT NULL,
fan_system TEXT NOT NULL,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
fan_power_allowance NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_FAN_POWER_ALLOWANCE_RECORD = """
    INSERT INTO %s (
template, 
air_system,
air_system_component,
fan_system,
minimum_capacity,
maximum_capacity,
fan_power_allowance,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "air_system": "",
    "air_system_component": "",
    "fan_system": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "fan_power_allowance": 0.0,
    "annotation": "",
}


class SystemRequirementsFanPowerAllowance(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementsFanPowerAllowance, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_FAN_POWER_ALLOWANCE_TABLE
            % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_FAN_POWER_ALLOWANCE_RECORD
            % table_name,
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
            "air_system",
            "air_system_component",
            "fan_system",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_capacity",
            "maximum_capacity",
            "fan_power_allowance",
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
            getattr_either("template", record),
            getattr_either("air_system", record),
            getattr_either("air_system_component", record),
            getattr_either("fan_system", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("fan_power_allowance", record),
            getattr_either("annotation", record),
        )
