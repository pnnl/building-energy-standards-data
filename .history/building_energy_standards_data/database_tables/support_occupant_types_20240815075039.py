from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_occupant_types"

RECORD_HELP = """
Must provide a dict that contains following key value pairs:
ventilation_space_type_name: TEXT
name: TEXT
category: TEXT
form: TEXT
dependent_variable: TEXT
independent_variable_1: TEXT
independent_variable_2: TEXT
coeff_1: NUMERIC
coeff_2: NUMERIC
coeff_3: NUMERIC
coeff_4: NUMERIC
coeff_5: NUMERIC
coeff_6: NUMERIC
coeff_7: NUMERIC
coeff_8: NUMERIC
coeff_9: NUMERIC
coeff_10: NUMERIC
minimum_independent_variable_1: NUMERIC
maximum_independent_variable_1: NUMERIC
minimum_independent_variable_2: NUMERIC
maximum_independent_variable_2: NUMERIC
minimum_dependent_variable_output: NUMERIC
maximum_dependent_variable_output: NUMERIC
annotation: TEXT
"""

CREATE_OCCUPANT_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS occupant_type (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    occupant_control TEXT NOT NULL,
    energy_behavior_wasteful TEXT,
    energy_behavior_normal TEXT,
    energy_behavior_austerity TEXT,
    occupant_schedule_early_bird TEXT,
    occupant_schedule_early_bird_fraction NUMERIC,
    occupant_schedule_regular_worker TEXT,
    occupant_schedule_regular_worker_fraction NUMERIC,
    occupant_schedule_late_owl TEXT,
    occupant_schedule_late_owl_fraction NUMERIC,
    occupant_schedule_night_shift TEXT,
    occupant_schedule_night_shift_fraction NUMERIC
);
"""

INSERT_OCCUPANT_TYPE = """
    INSERT INTO occupant_type
    (name, occupant_control, energy_behavior_wasteful, energy_behavior_normal, energy_behavior_austerity,
     occupant_schedule_early_bird, occupant_schedule_early_bird_fraction, 
     occupant_schedule_regular_worker, occupant_schedule_regular_worker_fraction, 
     occupant_schedule_late_owl, occupant_schedule_late_owl_fraction, 
     occupant_schedule_night_shift, occupant_schedule_night_shift_fraction)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""


RECORD_TEMPLATE ={ 
"name": "",
"occupant_control": "",
"energy_behavior_wasteful": "",
"energy_behavior_normal": "",
"energy_behavior_austerity": "",
"occupant_schedule_early_bird": "",
"occupant_schedule_early_bird_fraction": 0.0,
"occupant_schedule_regular_worker": "",
"occupant_schedule_regular_worker_fraction": 0.0,
"occupant_schedule_late_owl": "",
"occupant_schedule_late_owl_fraction": 0.0,
"occupant_schedule_night_shift": "",
"occupant_schedule_night_shift_fraction": 0.0
},


class SupportOccupantTypeTable(DBOperation):
    def __init__(self):
         super(SupportOccupantTypeTable, self).__init__(
            table_name=TABLE_NAME,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
            create_table_query=CREATE_OCCUPANT_TYPE_TABLE % TABLE_NAME,
            insert_record_query=INSERT_OCCUPANT_TYPE % TABLE_NAME,
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
            "occupant_control",
            "energy_behavior_wasteful",
            "energy_behavior_normal",
            "energy_behavior_austerity",
            "occupant_schedule_early_bird",
            "occupant_schedule_regular_worker",
            "occupant_schedule_late_owl",
            "occupant_schedule_night_shift"
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "occupant_schedule_early_bird_fraction",
            "occupant_schedule_regular_worker_fraction",
            "occupant_schedule_late_owl_fraction",
            "occupant_schedule_night_shift_fraction"
        ]

        for f in float_expected:
            if record.get(f):
                assert is_float(
                    record.get(f)
                ), f"{f} requires to be numeric data type, instead got {record[f]}"

        for i in range(10):
            if record.get(f"coeff_{i+1}"):
                coeff = f"coeff_{i+1}"
                record_id = record[f"{coeff}"]
                assert is_float(
                    record.get(coeff)
                ), f"{coeff} requires to be numeric data type, instead got {record_id}"
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
            getattr_either("occupant_schedule_night_shift_fraction", record)
        )