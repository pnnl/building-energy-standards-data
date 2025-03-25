import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_unitary_air_conditioners import (
    HVACMinimumRequirementUnitaryAirConditioners,
)

TABLE_NAME = "hvac_minimum_requirements_unitary_air_conditioners_189_1"


class HVACMinimumRequirementUnitaryAirConditioners1891Table(
    HVACMinimumRequirementUnitaryAirConditioners
):
    def __init__(self):
        super(HVACMinimumRequirementUnitaryAirConditioners1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
