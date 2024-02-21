import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirement_heat_pump_heating import (
    HVACMinimumRequirementHeatPumpHeating,
)

TABLE_NAME = "hvac_minimum_requirement_heat_pump_heating_90_1_prm"


class HVACMinimumRequirementHeatPumpHeating901PRMTable(
    HVACMinimumRequirementHeatPumpHeating
):
    def __init__(self):
        super(HVACMinimumRequirementHeatPumpHeating901PRMTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
