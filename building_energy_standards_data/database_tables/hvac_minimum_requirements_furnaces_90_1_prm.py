import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_furnaces import (
    HVACMinimumRequirementFurnaces,
)

TABLE_NAME = "hvac_minimum_requirements_furnaces_90_1_prm"


class HVACMinimumRequirementFurnaces901PRMTable(HVACMinimumRequirementFurnaces):
    def __init__(self):
        super(HVACMinimumRequirementFurnaces901PRMTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
