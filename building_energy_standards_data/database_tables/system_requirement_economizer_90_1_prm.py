import sqlite3

from building_energy_standards_data.database_tables.system_requirement_economizer import (
    SystemRequirementEconomizer,
)

TABLE_NAME = "system_requirement_economizer_90_1_prm"


class SystemRequirementEconomizer901PRMTable(SystemRequirementEconomizer):
    def __init__(self):
        super(SystemRequirementEconomizer901PRMTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
