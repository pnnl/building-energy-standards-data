import sqlite3

from building_energy_standards_data.database_tables.envelope_requirements import (
    EnvelopeRequirement,
)

TABLE_NAME = "envelope_requirements_189_1"


class EnvelopeRequirement1891Table(EnvelopeRequirement):
    def __init__(self):
        super(EnvelopeRequirement1891Table, self).__init__(
            table_name=TABLE_NAME,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
        )
