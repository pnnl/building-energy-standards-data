import sqlite3

from building_energy_standards_data.database_tables.level_3_lighting_90_1_definition import (
    LightDef901,
)

TABLE_NAME = "level_3_lighting_189_1_2017"


class LightDef18912017Table(LightDef901):
    def __init__(self):
        super(LightDef18912017Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
