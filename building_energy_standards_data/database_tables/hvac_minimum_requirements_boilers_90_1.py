import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_boilers import (
    HVACMinReqBoilers,
)

TABLE_NAME = "hvac_minimum_requirements_boilers_90_1"


class HVACMinReqBoilers901Table(HVACMinReqBoilers):
    def __init__(self):
        super(HVACMinReqBoilers901Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
