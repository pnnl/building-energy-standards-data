import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_water_heaters import (
    HVACMinimumRequirementWaterHeaters,
)

TABLE_NAME = "hvac_minimum_requirements_water_heaters_IECC"


class HVACMinimumRequirementWaterHeatersIECCTable(HVACMinimumRequirementWaterHeaters):
    def __init__(self):
        super(HVACMinimumRequirementWaterHeatersIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
