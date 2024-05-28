import sqlite3

from building_energy_standards_data.database_tables.level_3_lighting_90_1_prm_definition import (
    LightDef901PRM,
)

TABLE_NAME = "level_3_lighting_90_1_2013_prm"


class LightDef901PRM2013Table(LightDef901PRM):
    def __init__(self):
        super(LightDef901PRM2013Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
