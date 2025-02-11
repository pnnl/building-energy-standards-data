import sqlite3

from building_energy_standards_data.database_tables.envelope_thermal_bridging_requirements import (
    EnvelopeThermalBridgingRequirement,
)

TABLE_NAME = "envelope_thermal_bridging_requirements_IECC"


class EnvelopeThermalBridgingRequirementIECCTable(EnvelopeThermalBridgingRequirement):
    def __init__(self):
        super(EnvelopeThermalBridgingRequirementIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
