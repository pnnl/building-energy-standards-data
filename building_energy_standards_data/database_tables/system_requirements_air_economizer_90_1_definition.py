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
minimum_capacity: NUMERIC
fan_cooling_application: TEXT
minimum_water_cooled_chilled_water_capacity_no_fan_cooling: NUMERIC
minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling: NUMERIC
fixed_dry_bulb_is_allowed: TEXT
differential_dry_bulb_is_allowed: TEXT
electronic_enthalpy_is_allowed: TEXT
differential_enthalpy_is_allowed: TEXT
dew_point_dry_bulb_is_allowed: TEXT
fixed_enthalpy_is_allowed: TEXT
fixed_enthalpy_fixed_dry_bulb_is_allowed: TEXT
differential_enthalpy_fixed_dry_bulb_is_allowed: TEXT
fixed_dry_bulb_high_limit_shutoff_temp: NUMERIC
fixed_enthalpy_high_limit_shutoff_enthalpy: NUMERIC
dew_point_dry_bulb_high_limit_shutoff_dew_point_temp: NUMERIC
dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp: NUMERIC
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy: NUMERIC
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp: NUMERIC
differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp: NUMERIC
percent_increase_cooling_efficiency_eliminate_requirement: NUMERIC
heat_recovery_exempted: TEXT
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_air_economizer_90_1_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
climate_zone TEXT NOT NULL,
data_center TEXT,
minimum_capacity NUMERIC,
fan_cooling_application TEXT,
minimum_water_cooled_chilled_water_capacity_no_fan_cooling NUMERIC,
minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling NUMERIC,
fixed_dry_bulb_is_allowed TEXT,
differential_dry_bulb_is_allowed TEXT,
electronic_enthalpy_is_allowed TEXT,
differential_enthalpy_is_allowed TEXT,
dew_point_dry_bulb_is_allowed TEXT,
fixed_enthalpy_is_allowed TEXT,
fixed_enthalpy_fixed_dry_bulb_is_allowed TEXT,
differential_enthalpy_fixed_dry_bulb_is_allowed TEXT,
fixed_dry_bulb_high_limit_shutoff_temp NUMERIC,
fixed_enthalpy_high_limit_shutoff_enthalpy NUMERIC,
dew_point_dry_bulb_high_limit_shutoff_dew_point_temp NUMERIC,
dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp NUMERIC,
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy NUMERIC,
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp NUMERIC,
differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp NUMERIC,
percent_increase_cooling_efficiency_eliminate_requirement NUMERIC,
heat_recovery_exempted TEXT,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_ECONOMIZER = """
    INSERT INTO %s (
template,
climate_zone,
data_center,
minimum_capacity,
fan_cooling_application,
minimum_water_cooled_chilled_water_capacity_no_fan_cooling,
minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling,
fixed_dry_bulb_is_allowed,
differential_dry_bulb_is_allowed,
electronic_enthalpy_is_allowed,
differential_enthalpy_is_allowed,
dew_point_dry_bulb_is_allowed,
fixed_enthalpy_is_allowed,
fixed_enthalpy_fixed_dry_bulb_is_allowed,
differential_enthalpy_fixed_dry_bulb_is_allowed,
fixed_dry_bulb_high_limit_shutoff_temp,
fixed_enthalpy_high_limit_shutoff_enthalpy,
dew_point_dry_bulb_high_limit_shutoff_dew_point_temp,
dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp,
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy,
fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp,
differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp,
percent_increase_cooling_efficiency_eliminate_requirement,
heat_recovery_exempted,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "climate_zone": "",
    "data_center": "",
    "minimum_capacity": 0.0,
    "fan_cooling_application": "",
    "minimum_water_cooled_chilled_water_capacity_no_fan_cooling": 0.0,
    "minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling": 0.0,
    "fixed_dry_bulb_is_allowed": "",
    "differential_dry_bulb_is_allowed": "",
    "electronic_enthalpy_is_allowed": "",
    "differential_enthalpy_is_allowed": "",
    "dew_point_dry_bulb_is_allowed": "",
    "fixed_enthalpy_is_allowed": "",
    "fixed_enthalpy_fixed_dry_bulb_is_allowed": "",
    "differential_enthalpy_fixed_dry_bulb_is_allowed": "",
    "fixed_dry_bulb_high_limit_shutoff_temp": 0.0,
    "fixed_enthalpy_high_limit_shutoff_enthalpy": 0.0,
    "dew_point_dry_bulb_high_limit_shutoff_dew_point_temp": 0.0,
    "dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp": 0.0,
    "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy": 0.0,
    "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp": 0.0,
    "differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp": 0.0,
    "percent_increase_cooling_efficiency_eliminate_requirement": 0.0,
    "heat_recovery_exempted": "",
    "annotation": "",
}


class SystemRequirementEconomizer901(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementEconomizer901, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_air_economizer_90_1_TABLE
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
            "fan_cooling_application",
            "fixed_dry_bulb_is_allowed",
            "differential_dry_bulb_is_allowed",
            "electronic_enthalpy_is_allowed",
            "differential_enthalpy_is_allowed",
            "dew_point_dry_bulb_is_allowed",
            "fixed_enthalpy_is_allowed",
            "fixed_enthalpy_fixed_dry_bulb_is_allowed",
            "differential_enthalpy_fixed_dry_bulb_is_allowed",
            "heat_recovery_exempted",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_capacity",
            "minimum_water_cooled_chilled_water_capacity_no_fan_cooling",
            "minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling",
            "fixed_dry_bulb_high_limit_shutoff_temp",
            "fixed_enthalpy_high_limit_shutoff_enthalpy",
            "dew_point_dry_bulb_high_limit_shutoff_dew_point_temp",
            "dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp",
            "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy",
            "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp",
            "differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp",
            "percent_increase_cooling_efficiency_eliminate_requirement",
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
            getattr_either("minimum_capacity", record),
            getattr_either("fan_cooling_application", record),
            getattr_either(
                "minimum_water_cooled_chilled_water_capacity_no_fan_cooling", record
            ),
            getattr_either(
                "minimum_air_cooled_chilled_water_or_district_chilled_water_capacity_no_fan_cooling",
                record,
            ),
            getattr_either("fixed_dry_bulb_is_allowed", record),
            getattr_either("differential_dry_bulb_is_allowed", record),
            getattr_either("electronic_enthalpy_is_allowed", record),
            getattr_either("differential_enthalpy_is_allowed", record),
            getattr_either("dew_point_dry_bulb_is_allowed", record),
            getattr_either("fixed_enthalpy_is_allowed", record),
            getattr_either("fixed_enthalpy_fixed_dry_bulb_is_allowed", record),
            getattr_either("differential_enthalpy_fixed_dry_bulb_is_allowed", record),
            getattr_either("fixed_dry_bulb_high_limit_shutoff_temp", record),
            getattr_either("fixed_enthalpy_high_limit_shutoff_enthalpy", record),
            getattr_either(
                "dew_point_dry_bulb_high_limit_shutoff_dew_point_temp", record
            ),
            getattr_either(
                "dew_point_dry_bulb_high_limit_shutoff_dry_bulb_temp", record
            ),
            getattr_either(
                "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_enthalpy", record
            ),
            getattr_either(
                "fixed_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp", record
            ),
            getattr_either(
                "differential_enthalpy_fixed_dry_bulb_high_limit_shutoff_dry_bulb_temp",
                record,
            ),
            getattr_either(
                "percent_increase_cooling_efficiency_eliminate_requirement", record
            ),
            getattr_either("heat_recovery_exempted", record),
            getattr_either("annotation", record),
        )
