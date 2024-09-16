import sqlite3

conn = sqlite3.connect("openstudio_standards.db")
from building_energy_standards_data.applications.create_openstudio_standards_json import (
    create_openstudio_standards_data_json_ashrae_90_1,
)

for t in ["2004", "2007", "2010", "2013", "2016", "2019"]:
    create_openstudio_standards_data_json_ashrae_90_1(
        conn=conn,
        version_90_1=t,
        osstd_repository_path=r"",
    )
conn.close()
