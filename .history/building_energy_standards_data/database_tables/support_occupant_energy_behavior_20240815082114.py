from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_energy_behaviors"

RECORD_HELP = """
Must provide a dict that contains following key value pairs:
name TEXT NOT NULL,
category TEXT NOT NULL,
cooling_setpoint NUMERIC,
cooling_setpoint_units TEXT,
heating_setpoint NUMERIC,
heating_setpoint_units TEXT,
Minimum_Input_Power_Fraction_for_Continuous_Dimming_Control NUMERIC,
Minimum_Light_Output_Fraction_for_Continuous_Dimming_Control NUMERIC
"""

CREATE_ENERGY_BEHAVIOR_TABLE = """
CREATE TABLE IF NOT EXISTS support_energy_behaviors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    cooling_setpoint NUMERIC,
    cooling_setpoint_units TEXT,
    heating_setpoint NUMERIC,
    heating_setpoint_units TEXT,
    Minimum_Input_Power_Fraction_for_Continuous_Dimming_Control NUMERIC,
    Minimum_Light_Output_Fraction_for_Continuous_Dimming_Control NUMERIC
);
"""

INSERT_ENERGY_BEHAVIOR = """
    INSERT INTO support_energy_behaviors
    (name, category, cooling_setpoint, cooling_setpoint_units,
     heating_setpoint, heating_setpoint_units,
     Minimum_Input_Power_Fraction_for_Continuous_Dimming_Control,
     Minimum_Light_Output_Fraction_for_Continuous_Dimming_Control)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "name": "",
    "category": "",
    "cooling_setpoint": 0.0,
    "cooling_setpoint_units": "",
    "heating_setpoint": 0.0,
    "heating_setpoint_units": "",
    "Minimum_Input_Power_Fraction_for_Continuous_Dimming_Control": 0.0,
    "Minimum_Light_Output_Fraction_for_Continuous_Dimming_Control": 0.0,
}



class SupportEnergyBehaviorTable(DBOperation):
    def __init__(self):
        super(SupportEnergyBehaviorTable, self).__init__(
            table_name=TABLE_NAME,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
            create_table_query=CREATE_ENERGY_BEHAVIOR_TABLE % TABLE_NAME,
            insert_record_query=INSERT_ENERGY_BEHAVIOR % TABLE_NAME,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "name",
            "category",
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
            "Minimum_Input_Power_Fraction_for_Continuous_Dimming_Control",
            "Minimum_Light_Output_Fraction_for_Continuous_Dimming_Control",
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
            getattr_either("name", record),
            getattr_either("occupant_control", record),
            getattr_either("energy_behavior_wasteful", record),
            getattr_either("energy_behavior_normal", record),
            getattr_either("energy_behavior_austerity", record),
            getattr_either("occupant_schedule_early_bird", record),
            getattr_either("occupant_schedule_early_bird_fraction", record),
            getattr_either("occupant_schedule_regular_worker", record),
            getattr_either("occupant_schedule_regular_worker_fraction", record),
            getattr_either("occupant_schedule_late_owl", record),
            getattr_either("occupant_schedule_late_owl_fraction", record),
            getattr_either("occupant_schedule_night_shift", record),
            getattr_either("occupant_schedule_night_shift_fraction", record),
        )