import sqlite3

from building_energy_standards_data.database_tables.exterior_lighting_definition import (
    ExtLightDef,
)

TABLE_NAME = "exterior_lighting_189_1"


class ExtLightDef1891Table(ExtLightDef):
    def __init__(self):
        super(ExtLightDef1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
