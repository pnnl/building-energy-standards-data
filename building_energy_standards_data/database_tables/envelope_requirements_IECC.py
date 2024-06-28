import sqlite3

from building_energy_standards_data.database_tables.envelope_requirements import (
    EnvelopeRequirement,
)

TABLE_NAME = "envelope_requirements_IECC"


class EnvelopeRequirementIECCTable(EnvelopeRequirement):
    def __init__(self):
        super(EnvelopeRequirementIECCTable, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
