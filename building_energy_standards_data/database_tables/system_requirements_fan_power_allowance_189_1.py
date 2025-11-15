import sqlite3

from building_energy_standards_data.database_tables.system_requirements_fan_power_allowance import (
    SystemRequirementsFanPowerAllowance,
)

TABLE_NAME = "system_requirements_fan_power_allowance_189_1"


class SystemRequirementsFanPowerAllowance1891Table(SystemRequirementsFanPowerAllowance):
    def __init__(self):
        super(SystemRequirementsFanPowerAllowance1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
