import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirement_water_source_heat_pumps_cooling import (
    HVACMinimumRequirementWaterSourceHeatPumpsCooling,
)

TABLE_NAME = "hvac_minimum_requirement_water_source_heat_pumps_cooling_90_1"


class HVACMinimumRequirementWaterSourceHeatPumpsCooling901Table(
    HVACMinimumRequirementWaterSourceHeatPumpsCooling
):
    def __init__(self):
        super(HVACMinimumRequirementWaterSourceHeatPumpsCooling901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
