import sqlite3

from database_tables.level_3_lighting_90_1_definition import LightDef901

TABLE_NAME = "level_3_lighting_90_1_2007"


class LightDef9012007Table(LightDef901):
    def __init__(self):
        super(LightDef9012007Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"database_files/{TABLE_NAME}",
        )