import sqlite3

from database_tables.level_3_ventilation_62_1_definition import VentDef621

TABLE_NAME = "level_3_ventilation_62_1_2016"


class VentDef6212016Table(VentDef621):
    def __init__(self):
        super(VentDef6212016Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"database_files/{TABLE_NAME}",
        )