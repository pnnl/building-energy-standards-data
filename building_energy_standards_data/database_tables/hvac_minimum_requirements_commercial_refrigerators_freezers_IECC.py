import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_commercial_refrigerators_freezers import (
    HVACMinimumRequirementRefrigeratorsFreezers,
)

TABLE_NAME = "hvac_minimum_requirements_commercial_refrigerators_freezers_IECC"


class HVACMinimumRequirementRefrigeratorsFreezersIECCTable(
    HVACMinimumRequirementRefrigeratorsFreezers
):
    def __init__(self):
        super(HVACMinimumRequirementRefrigeratorsFreezersIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
