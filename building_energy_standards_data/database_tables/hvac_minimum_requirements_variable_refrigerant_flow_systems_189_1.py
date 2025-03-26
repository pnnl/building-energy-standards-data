import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_variable_refrigerant_flow_systems import (
    HVACMinimumRequirementVRF,
)

TABLE_NAME = "hvac_minimum_requirements_variable_refrigerant_flow_systems_189_1"


class HVACMinimumRequirementVRF1891Table(HVACMinimumRequirementVRF):
    def __init__(self):
        super(HVACMinimumRequirementVRF1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
