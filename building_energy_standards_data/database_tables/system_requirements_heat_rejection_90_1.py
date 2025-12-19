import sqlite3

from building_energy_standards_data.database_tables.system_requirements_heat_rejection import (
    SystemRequirementsHeatRejection,
)

TABLE_NAME = "system_requirements_heat_rejection_90_1"


class SystemRequirementsHeatRejection901Table(SystemRequirementsHeatRejection):
    def __init__(self):
        super(SystemRequirementsHeatRejection901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
