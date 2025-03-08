import sqlite3

from building_energy_standards_data.database_tables.system_requirements_fan_power_allowance import (
    SystemRequirementsFanPowerAllowance,
)

TABLE_NAME = "system_requirements_fan_power_allowance_90_1"


class SystemRequirementsFanPowerAllowance901Table(SystemRequirementsFanPowerAllowance):
    def __init__(self):
        super(SystemRequirementsFanPowerAllowance901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
