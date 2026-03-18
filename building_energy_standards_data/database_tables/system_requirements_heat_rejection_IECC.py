import sqlite3

from building_energy_standards_data.database_tables.system_requirements_heat_rejection import (
    SystemRequirementsHeatRejection,
)

TABLE_NAME = "system_requirements_heat_rejection_IECC"


class SystemRequirementsHeatRejectionIECCTable(SystemRequirementsHeatRejection):
    def __init__(self):
        super(SystemRequirementsHeatRejectionIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
