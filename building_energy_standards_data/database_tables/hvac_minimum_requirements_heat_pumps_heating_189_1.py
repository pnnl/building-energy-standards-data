import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_heat_pumps_heating import (
    HVACMinimumRequirementHeatPumpHeating,
)

TABLE_NAME = "hvac_minimum_requirements_heat_pumps_heating_189_1"


class HVACMinimumRequirementHeatPumpHeating1891Table(
    HVACMinimumRequirementHeatPumpHeating
):
    def __init__(self):
        super(HVACMinimumRequirementHeatPumpHeating1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
