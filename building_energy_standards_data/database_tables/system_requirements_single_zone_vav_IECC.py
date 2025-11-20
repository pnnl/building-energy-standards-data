import sqlite3

from building_energy_standards_data.database_tables.system_requirements_single_zone_vav import (
    SystemRequirementSingleZoneVAV,
)

TABLE_NAME = "system_requirements_single_zone_vav_IECC"


class SystemRequirementSingleZoneVAVIECCTable(SystemRequirementSingleZoneVAV):
    def __init__(self):
        super(SystemRequirementSingleZoneVAVIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
