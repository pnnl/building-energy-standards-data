import sqlite3

from building_energy_standards_data.database_tables.level_3_ventilation_62_1_definition import (
    VentDef621,
)

TABLE_NAME = "level_3_ventilation_62_1_2007"


class VentDef6212007Table(VentDef621):
    def __init__(self):
        super(VentDef6212007Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
