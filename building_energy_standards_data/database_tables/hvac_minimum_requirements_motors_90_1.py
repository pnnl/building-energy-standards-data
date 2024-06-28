import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_motors import (
    HVACMinimumRequirementMotors,
)

TABLE_NAME = "hvac_minimum_requirements_motors_90_1"


class HVACMinimumRequirementMotors901Table(HVACMinimumRequirementMotors):
    def __init__(self):
        super(HVACMinimumRequirementMotors901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
