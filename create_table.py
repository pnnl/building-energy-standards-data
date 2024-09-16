import sqlite3
from building_energy_standards_data.applications.database_maintenance import (
    create_openstudio_standards_database_from_json,
)

conn = sqlite3.connect("openstudio_standards_test.db")
create_openstudio_standards_database_from_json(conn)
conn.close()
