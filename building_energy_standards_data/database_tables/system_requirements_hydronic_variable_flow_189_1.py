import sqlite3

from building_energy_standards_data.database_tables.system_requirements_hydronic_variable_flow import (
    SystemRequirementsHydronicVariableFlow,
)

TABLE_NAME = "system_requirements_hydronic_variable_flow_189_1"


class SystemRequirementsHydronicVariableFlow1891Table(
    SystemRequirementsHydronicVariableFlow
):
    def __init__(self):
        super(SystemRequirementsHydronicVariableFlow1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
