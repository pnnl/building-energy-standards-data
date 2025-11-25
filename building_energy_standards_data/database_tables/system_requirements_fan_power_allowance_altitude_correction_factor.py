from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
minimum_altitude: NUMERIC
maximum_altitude: NUMERIC
correction_factor: NUMERIC
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_fan_control_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
minimum_altitude NUMERIC,
maximum_altitude NUMERIC,
correction_factor NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_fan_control_RECORD = """
    INSERT INTO %s (
template, 
minimum_altitude,
maximum_altitude,
correction_factor,
annotation
) 
VALUES (?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "minimum_altitude": "",
    "maximum_altitude": "",
    "correction_factor": "",
    "annotation": "",
}


class SystemRequirementFanPowerAllowanceAltitudeCorrectionFactor(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementFanPowerAllowanceAltitudeCorrectionFactor, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_fan_control_TABLE
            % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_fan_control_RECORD
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
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_altitude",
            "maximum_altitude",
            "correction_factor"
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
            getattr_either("minimum_altitude", record),
            getattr_either("maximum_altitude", record),
            getattr_either("correction_factor", record),
            getattr_either("annotation", record),
        )
