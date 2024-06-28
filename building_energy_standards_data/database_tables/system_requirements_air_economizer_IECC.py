import sqlite3

from building_energy_standards_data.database_tables.system_requirements_air_economizer_IECC_definition import (
    SystemRequirementEconomizerIECC,
)

TABLE_NAME = "system_requirements_air_economizer_IECC"


class SystemRequirementEconomizerIECCTable(SystemRequirementEconomizerIECC):
    def __init__(self):
        super(SystemRequirementEconomizerIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
