from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
climate_zone: TEXT
data_center: TEXT
systems_3_4_minimum_threshold: NUMERIC
systems_3_4_minimum_threshold_descriptor: TEXT
systems_5_through_8_minimum_threshold: NUMERIC
systems_5_through_8_minimum_threshold_descriptor: TEXT
systems_11_12_13_minimum_threshold: NUMERIC
systems_11_12_13_minimum_threshold_descriptor: TEXT
allowed_control_type: TEXT
fixed_dry_bulb_high_limit_shutoff_temp: NUMERIC
fixed_enthalpy_high_limit_shutoff_enthalpy: NUMERIC
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_air_economizer_90_1_PRM_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
climate_zone TEXT NOT NULL,
data_center TEXT,
systems_3_4_minimum_threshold NUMERIC,
systems_3_4_minimum_threshold_descriptor TEXT,
systems_5_through_8_minimum_threshold NUMERIC,
systems_5_through_8_minimum_threshold_descriptor TEXT,
systems_11_12_13_minimum_threshold NUMERIC,
systems_11_12_13_minimum_threshold_descriptor TEXT,
allowed_control_type TEXT,
fixed_dry_bulb_high_limit_shutoff_temp NUMERIC,
fixed_enthalpy_high_limit_shutoff_enthalpy NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_ECONOMIZER = """
    INSERT INTO %s (
template,
climate_zone,
data_center,
systems_3_4_minimum_threshold,
systems_3_4_minimum_threshold_descriptor,
systems_5_through_8_minimum_threshold,
systems_5_through_8_minimum_threshold_descriptor,
systems_11_12_13_minimum_threshold,
systems_11_12_13_minimum_threshold_descriptor,
allowed_control_type,
fixed_dry_bulb_high_limit_shutoff_temp,
fixed_enthalpy_high_limit_shutoff_enthalpy,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "climate_zone": "",
    "data_center": "",
    "systems_3_4_minimum_threshold": 0.0,
    "systems_3_4_minimum_threshold_descriptor": "",
    "systems_5_through_8_minimum_threshold": 0.0,
    "systems_5_through_8_minimum_threshold_descriptor": "",
    "systems_11_12_13_minimum_threshold": 0.0,
    "systems_11_12_13_minimum_threshold_descriptor": "",
    "allowed_control_type": "",
    "fixed_dry_bulb_high_limit_shutoff_temp": 0.0,
    "fixed_enthalpy_high_limit_shutoff_enthalpy": 0.0,
    "annotation": "",
}


class SystemRequirementEconomizer901PRM(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementEconomizer901PRM, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_air_economizer_90_1_PRM_TABLE
            % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_ECONOMIZER % table_name,
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
            "climate_zone",
            "data_center",
            "systems_3_4_minimum_threshold_descriptor",
            "systems_5_through_8_minimum_threshold_descriptor",
            "systems_11_12_13_minimum_threshold_descriptor",
            "allowed_control_type",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "systems_3_4_minimum_threshold",
            "systems_5_through_8_minimum_threshold",
            "systems_11_12_13_minimum_threshold",
            "fixed_dry_bulb_high_limit_shutoff_temp",
            "fixed_enthalpy_high_limit_shutoff_enthalpy",
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
            getattr_either("climate_zone", record),
            getattr_either("data_center", record),
            getattr_either("systems_3_4_minimum_threshold", record),
            getattr_either("systems_3_4_minimum_threshold_descriptor", record),
            getattr_either("systems_5_through_8_minimum_threshold", record),
            getattr_either("systems_5_through_8_minimum_threshold_descriptor", record),
            getattr_either("systems_11_12_13_minimum_threshold", record),
            getattr_either("systems_11_12_13_minimum_threshold_descriptor", record),
            getattr_either("allowed_control_type", record),
            getattr_either("fixed_dry_bulb_high_limit_shutoff_temp", record),
            getattr_either("fixed_enthalpy_high_limit_shutoff_enthalpy", record),
            getattr_either("annotation", record),
        )
