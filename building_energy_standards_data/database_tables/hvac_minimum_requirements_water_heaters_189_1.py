import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_water_heaters import (
    HVACMinimumRequirementWaterHeaters,
)

TABLE_NAME = "hvac_minimum_requirements_water_heaters_189_1"


class HVACMinimumRequirementWaterHeaters1891Table(HVACMinimumRequirementWaterHeaters):
    def __init__(self):
        super(HVACMinimumRequirementWaterHeaters1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
