import sqlite3

from database_tables.hvac_minimum_requirement_water_heaters import (
    HVACMinimumRequirementWaterHeaters,
)

TABLE_NAME = "hvac_minimum_requirement_water_heaters_90_1_prm"


class HVACMinimumRequirementWaterHeaters901prmTable(HVACMinimumRequirementWaterHeaters):
    def __init__(self):
        super(HVACMinimumRequirementWaterHeaters901prmTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"database_files/{TABLE_NAME}",
        )
