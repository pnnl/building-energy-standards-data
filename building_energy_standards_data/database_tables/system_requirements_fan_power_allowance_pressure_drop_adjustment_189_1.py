import sqlite3

from building_energy_standards_data.database_tables.system_requirements_fan_power_allowance_pressure_drop_adjustment import (
    SystemRequirementsFanPowerAllowancePressureDropAdjustment,
)

TABLE_NAME = "system_requirements_fan_power_allowance_pressure_drop_adjustment_189_1"


class SystemRequirementsFanPowerAllowancePressureDropAdjustment1891Table(
    SystemRequirementsFanPowerAllowancePressureDropAdjustment
):
    def __init__(self):
        super(
            SystemRequirementsFanPowerAllowancePressureDropAdjustment1891Table, self
        ).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
