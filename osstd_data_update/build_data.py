import os

print(os.getcwd())
import sqlite3

if not os.path.isfile("openstudio_standards.db"):
    print("openstudio_standards.db does not exist, generating db first")
    from building_energy_standards_data.applications.database_maintenance import (
        create_openstudio_standards_database_from_json,
    )

    conn = sqlite3.connect("openstudio_standards.db")
    create_openstudio_standards_database_from_json(conn)
    conn.close()
    if os.path.isfile("openstudio_standards.db"):
        print("openstudio_standards.db generated")
    else:
        print("Error in generating openstudio_standards.db")

conn = sqlite3.connect("openstudio_standards.db")

from building_energy_standards_data.applications.create_openstudio_standards_json import (
    create_openstudio_standards_data_json_ashrae_90_1,
)

for t in ["2004", "2007", "2010", "2013", "2016", "2019"]:
    create_openstudio_standards_data_json_ashrae_90_1(
        conn=conn, version_90_1=t, osstd_repository_path="../openstudio-standards"
    )
conn.close()


for t in ["2019"]:
    create_openstudio_standards_data_json_ashrae_90_1(
        conn=conn, version_90_1=t, osstd_repository_path="../OSSTD-T1.1", prm=True
    )
conn.close()
