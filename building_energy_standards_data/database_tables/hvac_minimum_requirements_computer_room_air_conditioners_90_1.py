import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_computer_room_air_conditioners import (
    HVACMinimumRequirementComputerRoomAirConditioners,
)

TABLE_NAME = "hvac_minimum_requirements_computer_room_air_conditioners_90_1"


class HVACMinimumRequirementComputerRoomAirConditioners901Table(
    HVACMinimumRequirementComputerRoomAirConditioners
):
    def __init__(self):
        super(HVACMinimumRequirementComputerRoomAirConditioners901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
