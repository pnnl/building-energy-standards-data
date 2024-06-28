import sqlite3

from building_energy_standards_data.database_tables.hvac_minimum_requirements_heat_rejection import (
    HVACMinimumRequirementHeatRejection,
)

TABLE_NAME = "hvac_minimum_requirements_heat_rejection_IECC"


class HVACMinimumRequirementHeatRejectionIECCTable(HVACMinimumRequirementHeatRejection):
    def __init__(self):
        super(HVACMinimumRequirementHeatRejectionIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
