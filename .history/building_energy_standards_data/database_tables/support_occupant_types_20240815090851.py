from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_occupant_types"

RECORD_HELP = """
Must provide a dict that contains following key value pairs:
name TEXT NOT NULL,
occupant_control TEXT NOT NULL,
energy_behavior TEXT,
occupant_schedule_early_bird_fraction NUMERIC,
occupant_schedule_early_bird_occupant_schedule TEXT,
occupant_schedule_regular_worker_fraction NUMERIC,
occupant_schedule_regular_worker_occupant_schedule TEXT,
occupant_schedule_late_owl_fraction NUMERIC,
occupant_schedule_late_owl_occupant_schedule TEXT,
occupant_schedule_night_shift_fraction NUMERIC,
occupant_schedule_night_shift_occupant_schedule TEXT
"""

CREATE_OCCUPANT_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS support_occupant_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    occupant_control TEXT NOT NULL,
    energy_behavior TEXT,
    occupant_schedule_early_bird_fraction NUMERIC,
    occupant_schedule_early_bird TEXT,
    occupant_schedule_regular_worker_fraction NUMERIC,
    occupant_schedule_regular_worker TEXT,
    occupant_schedule_late_owl_fraction NUMERIC,
    occupant_schedule_late_owl TEXT,
    occupant_schedule_night_shift_fraction NUMERIC,
    occupant_schedule_night_shift TEXT
);
"""

INSERT_OCCUPANT_TYPE = """
    INSERT INTO support_occupant_types
    (name, occupant_control, energy_behavior, 
     occupant_schedule_early_bird_fraction, occupant_schedule_early_bird, 
     occupant_schedule_regular_worker_fraction, occupant_schedule_regular_worker, 
     occupant_schedule_late_owl_fraction, occupant_schedule_late_owl, 
     occupant_schedule_night_shift_fraction, occupant_schedule_night_shift)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""


RECORD_TEMPLATE = {
    "name": "",
    "occupant_control": "",
    "energy_behavior": "",
    "occupant_schedule_early_bird_fraction": 0.0,
    "occupant_schedule_early_bird": "",
    "occupant_schedule_regular_worker_fraction": 0.0,
    "occupant_schedule_regular_worker": "",
    "occupant_schedule_late_owl_fraction": 0.0,
    "occupant_schedule_late_owl": "",
    "occupant_schedule_night_shift_fraction": 0.0,
    "occupant_schedule_night_shift": "",
}


class SupportOccupantTypeTable(DBOperation):
    def __init__(self):
        super(SupportOccupantTypeTable, self).__init__(
            table_name=TABLE_NAME,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
            create_table_query=CREATE_OCCUPANT_TYPE_TABLE,
            insert_record_query=INSERT_OCCUPANT_TYPE,
        )

    def get_record_info(self):
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "name",
            "occupant_control",
            "energy_behavior",
            "occupant_schedule_early_bird",
            "occupant_schedule_regular_worker",
            "occupant_schedule_late_owl",
            "occupant_schedule_night_shift",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(record[f], str), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "occupant_schedule_early_bird_fraction",
            "occupant_schedule_regular_worker_fraction",
            "occupant_schedule_late_owl_fraction",
            "occupant_schedule_night_shift_fraction",
        ]

        for f in float_expected:
            if record.get(f):
                assert is_float(record[f]), f"{f} requires to be numeric data type, instead got {record[f]}"

        return True

    def _preprocess_record(self, record):
        return (
            getattr_either("name", record),
            getattr_either("occupant_control", record),
            getattr_either("energy_behavior", record),
            getattr_either("occupant_schedule_early_bird_fraction", record),
             getattr_either("occupant_schedule_early_bird_occupant_schedule", record)
            getattr_either("occupant_schedule_regular_worker_occupant_schedule", record),
            getattr_either("occupant_schedule_regular_worker_fraction", record),
            getattr_either("occupant_schedule_late_owl_occupant_schedule", record),
            getattr_either("occupant_schedule_late_owl_fraction", record),
            getattr_either("occupant_schedule_night_shift_occupant_schedule", record),
            getattr_either("occupant_schedule_night_shift_fraction", record)
        )
