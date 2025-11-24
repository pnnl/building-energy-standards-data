import sqlite3

from building_energy_standards_data.database_tables.system_requirements_fan_control import (
    SystemRequirementSingleZoneVAV,
)

TABLE_NAME = "system_requirements_fan_control_IECC"


class SystemRequirementSingleZoneVAVIECCTable(SystemRequirementSingleZoneVAV):
    def __init__(self):
        super(SystemRequirementSingleZoneVAVIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
