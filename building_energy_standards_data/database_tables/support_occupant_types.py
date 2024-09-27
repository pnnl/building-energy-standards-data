from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_occupant_types"

RECORD_HELP = """
Must provide a dict that contains following key value pairs:
name TEXT NOT NULL,
energy_behavior TEXT, 
occupant_schedule TEXT,
occupant_physical_characteristics TEXT
"""

CREATE_OCCUPANT_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS support_occupant_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    energy_behavior TEXT NOT NULL,
    occupant_schedule TEXT NOT NULL,
    occupant_physical_characteristics TEXT NOT NULL,
    FOREIGN KEY(energy_behavior) REFERENCES support_occupant_energy_behavior(energy_behavior_name),
    FOREIGN KEY(occupant_physical_characteristics) REFERENCES support_occupant_physical_characteristics(physical_characteristic_name)
);
"""


INSERT_OCCUPANT_TYPE = """
    INSERT INTO support_occupant_types
    (name, energy_behavior, 
     occupant_schedule,
     occupant_physical_characteristics)
     VALUES (?, ?, ?, ?);
"""


RECORD_TEMPLATE = {
    "name": "",
    "enrgy_behavior": "",
    "occupant_schedule": "",
    "occupant_physical_characteristics": "",
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
            "name" "energy_behavior",
            "occupant_schedule",
            "occupant_physical_characteristics",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        return True

    def _preprocess_record(self, record):
        return (
            getattr_either("name", record),
            getattr_either("energy_behavior", record),
            getattr_either("occupant_schedule", record),
            getattr_either("occupant_physical_characteristics", record),
        )
