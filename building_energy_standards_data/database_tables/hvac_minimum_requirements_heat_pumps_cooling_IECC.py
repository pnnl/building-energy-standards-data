import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_heat_pumps_cooling import (
    HVACMinimumRequirementHeatPumpCooling,
)

TABLE_NAME = "hvac_minimum_requirements_heat_pumps_cooling_IECC"


class HVACMinimumRequirementHeatPumpCoolingIECCTable(
    HVACMinimumRequirementHeatPumpCooling
):
    def __init__(self):
        super(HVACMinimumRequirementHeatPumpCoolingIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
