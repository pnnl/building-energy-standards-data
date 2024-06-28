import sqlite3

from building_energy_standards_data.database_tables.system_requirements_air_economizer_90_1_definition import (
    SystemRequirementEconomizer901,
)

TABLE_NAME = "system_requirements_air_economizer_90_1"


class SystemRequirementEconomizer901Table(SystemRequirementEconomizer901):
    def __init__(self):
        super(SystemRequirementEconomizer901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
