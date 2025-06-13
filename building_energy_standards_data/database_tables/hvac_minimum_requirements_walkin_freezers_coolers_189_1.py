import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_walkin_freezers_coolers import (
    HVACMinimumRequirementWalkinFreezersCoolers,
)

TABLE_NAME = "hvac_minimum_requirements_walkin_freezers_coolers_189_1"


class HVACMinimumRequirementWalkinFreezersCoolers1891Table(
    HVACMinimumRequirementWalkinFreezersCoolers
):
    def __init__(self):
        super(HVACMinimumRequirementWalkinFreezersCoolers1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
