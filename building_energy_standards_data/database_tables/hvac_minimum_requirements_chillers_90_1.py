import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_chillers import (
    HVACMinimumRequirementChillers,
)

TABLE_NAME = "hvac_minimum_requirements_chillers_90_1"


class HVACMinimumRequirementChillers901Table(HVACMinimumRequirementChillers):
    def __init__(self):
        super(HVACMinimumRequirementChillers901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
