import sqlite3

from building_energy_standards_data.database_tables.level_3_lighting_90_1_definition import (
    LightDef901,
)

TABLE_NAME = "level_3_lighting_90_1_2004"


class LightDef9012004Table(LightDef901):
    def __init__(self):
        super(LightDef9012004Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
