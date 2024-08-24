import sqlite3

from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
method: [BA, CS, SS]
lighting_primary_space_type: TEXT
lighting_secondary_space_type: TEXT
lighting_power_density: REAL
lighting_power_density_unit: TEXT
supplemental_lighting_power_density: REAL
supplemental_lighting_power_density_unit: TEXT
rcr_threshold: NUMERIC
automatic_daylight_responsive_controls_for_sidelighting: TEXT
automatic_daylight_responsive_controls_for_toplighting: TEXT
automatic_partial_off: TEXT
automatic_full_off: TEXT
scheduled_shutoff: TEXT
manon_or_partauto: NUMERIC
occup_sensor_reduction: NUMERIC
occup_sensor_manon_or_partauto_reduction: NUMERIC
annotation: TEXT (optional)
"""

CREATE_LIGHT_DEF_90_1_PRM_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY,
method TEXT DEFAULT 'BA' NOT NULL,
lighting_primary_space_type TEXT,
lighting_secondary_space_type TEXT, 
lighting_power_density NUMERIC NOT NULL,
lighting_power_density_unit TEXT DEFAULT 'w/ft2' NOT NULL,
supplemental_lighting_power_density NUMERIC,
supplemental_lighting_power_density_unit TEXT,
rcr_threshold NUMERIC,
automatic_daylight_responsive_controls_for_sidelighting TEXT,
automatic_daylight_responsive_controls_for_toplighting TEXT,
automatic_partial_off TEXT,
automatic_full_off TEXT,
scheduled_shutoff TEXT,
manon_or_partauto NUMERIC,
occup_sensor_reduction NUMERIC,
occup_sensor_manon_or_partauto_reduction NUMERIC,
annotation TEXT);
"""

INSERT_A_LIGHT_RECORD = """
    INSERT INTO %s
    (
        method,
        lighting_primary_space_type,
        lighting_secondary_space_type,
        lighting_power_density,
        lighting_power_density_unit,
        supplemental_lighting_power_density,
        supplemental_lighting_power_density_unit,
        rcr_threshold,
        automatic_daylight_responsive_controls_for_sidelighting,
        automatic_daylight_responsive_controls_for_toplighting,
        automatic_partial_off,
        automatic_full_off,
        scheduled_shutoff,
        manon_or_partauto,
        occup_sensor_reduction,
        occup_sensor_manon_or_partauto_reduction,
        annotation
        )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "method": "",
    "lighting_primary_space_type": "",
    "lighting_secondary_space_type": "",
    "lighting_power_density": 0.0,
    "lighting_power_density_unit": "W/ft2",
    "supplemental_lighting_power_density": 0.0,
    "supplemental_lighting_power_density_unit": "W/ft2",
    "rcr_threshold": 0.0,
    "automatic_daylight_responsive_controls_for_sidelighting": "",
    "automatic_daylight_responsive_controls_for_toplighting": "",
    "automatic_partial_off": "",
    "automatic_full_off": "",
    "scheduled_shutoff": "",
    "manon_or_partauto": 0.0,
    "occup_sensor_reduction": 0.0,
    "occup_sensor_manon_or_partauto_reduction": 0.0,
    "annotation": "",
}


class LightDef901PRM(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(LightDef901PRM, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_LIGHT_DEF_90_1_PRM_TABLE % table_name,
            insert_record_query=INSERT_A_LIGHT_RECORD % table_name,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        if record.get("method"):
            assert record["method"] in [
                "BA",
                "CS",
                "SS",
            ], f"method is provided with wrong choice value. Available: BA, CS, SS "
        if record.get("lighting_per_area"):
            assert is_float(
                record.get("lighting_per_area")
            ), f"lighting_per_area requires to be numeric data type, instead got {record['lighting_per_area']}"
        return True

    def _preprocess_record(self, record):
        """

        :param record: dictionary
        :return:
        """
        record_tuple = (
            getattr_either("method", record),
            getattr_either("lighting_primary_space_type", record),
            getattr_either("lighting_secondary_space_type", record),
            getattr_either("lighting_power_density", record),
            getattr_either("lighting_power_density_unit", record, "W/ft2"),
            getattr_either("supplemental_lighting_power_density", record),
            getattr_either("supplemental_lighting_power_density_unit", record, "W/ft2"),
            getattr_either("rcr_threshold", record),
            getattr_either(
                "automatic_daylight_responsive_controls_for_sidelighting", record
            ),
            getattr_either(
                "automatic_daylight_responsive_controls_for_toplighting", record
            ),
            getattr_either("automatic_partial_off", record),
            getattr_either("automatic_full_off", record),
            getattr_either("scheduled_shutoff", record),
            getattr_either("manon_or_partauto", record),
            getattr_either("occup_sensor_reduction", record),
            getattr_either("occup_sensor_manon_or_partauto_reduction", record),
            getattr_either("annotation", record),
        )
        return record_tuple
