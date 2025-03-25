import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_heat_rejection import (
    HVACMinimumRequirementHeatRejection,
)

TABLE_NAME = "hvac_minimum_requirements_heat_rejection_189_1"


class HVACMinimumRequirementHeatRejection1891Table(HVACMinimumRequirementHeatRejection):
    def __init__(self):
        super(HVACMinimumRequirementHeatRejection1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
