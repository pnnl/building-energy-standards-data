import sqlite3

from building_energy_standards_data.database_tables.system_requirements_energy_recovery import (
    SystemRequirementEnergyRecovery,
)

TABLE_NAME = "system_requirements_energy_recovery_90_1_prm"


class SystemRequirementEnergyRecovery901PRMTable(SystemRequirementEnergyRecovery):
    def __init__(self):
        super(SystemRequirementEnergyRecovery901PRMTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
