import sqlite3

from building_energy_standards_data.database_tables.system_requirements_energy_recovery import (
    SystemRequirementEnergyRecovery,
)

TABLE_NAME = "system_requirements_energy_recovery_90_1"


class SystemRequirementEnergyRecovery901Table(SystemRequirementEnergyRecovery):
    def __init__(self):
        super(SystemRequirementEnergyRecovery901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
