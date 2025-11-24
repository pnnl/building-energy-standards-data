from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
start_date: TEXT
end_date: TEXT
cooling_capacity_threshold_for_single_zone_dx_vav: NUMERIC
fan_motor_size_hp_threshold_for_single_zone_dx_vav: NUMERIC
fan_motor_size_hp_threshold_for_vav_part_load_power_limitation: NUMERIC
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_fan_control_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
start_date TEXT,
end_date TEXT,
cooling_capacity_threshold_for_single_zone_dx_vav NUMERIC,
fan_motor_size_hp_threshold_for_single_zone_dx_vav NUMERIC,
fan_motor_size_hp_threshold_for_vav_part_load_power_limitation NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_fan_control_RECORD = """
    INSERT INTO %s (
template, 
start_date,
end_date,
cooling_capacity_threshold_for_single_zone_dx_vav,
fan_motor_size_hp_threshold_for_single_zone_dx_vav,
fan_motor_size_hp_threshold_for_vav_part_load_power_limitation,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "start_date": "",
    "end_date": "",
    "cooling_capacity_threshold_for_single_zone_dx_vav": 0.0,
    "fan_motor_size_hp_threshold_for_single_zone_dx_vav": 0.0,
    "fan_motor_size_hp_threshold_for_vav_part_load_power_limitation": 0.0,
    "annotation": "",
}


class SystemRequirementSingleZoneVAV(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementSingleZoneVAV, self).__init__(
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
            "start_date",
            "end_date",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "cooling_capacity_threshold_for_single_zone_dx_vav",
            "fan_motor_size_hp_threshold_for_single_zone_dx_vav",
            "fan_motor_size_hp_threshold_for_vav_part_load_power_limitation"
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
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("cooling_capacity_threshold_for_single_zone_dx_vav", record),
            getattr_either("fan_motor_size_hp_threshold_for_single_zone_dx_vav", record),
            getattr_either("fan_motor_size_hp_threshold_for_vav_part_load_power_limitation", record),
            getattr_either("annotation", record),
        )
