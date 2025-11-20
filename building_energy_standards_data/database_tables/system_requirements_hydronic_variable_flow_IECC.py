import sqlite3

from building_energy_standards_data.database_tables.system_requirements_hydronic_variable_flow import (
    SystemRequirementsHydronicVariableFlow,
)

TABLE_NAME = "system_requirements_hydronic_variable_flow_IECC"


class SystemRequirementsHydronicVariableFlowIECCTable(
    SystemRequirementsHydronicVariableFlow
):
    def __init__(self):
        super(SystemRequirementsHydronicVariableFlowIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
