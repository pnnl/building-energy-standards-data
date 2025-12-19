import sqlite3

from building_energy_standards_data.database_tables.system_requirements_heat_rejection import (
    SystemRequirementsHeatRejection,
)

TABLE_NAME = "system_requirements_heat_rejection_189_1"


class SystemRequirementsHeatRejection1891Table(SystemRequirementsHeatRejection):
    def __init__(self):
        super(SystemRequirementsHeatRejection1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
