# %%
import sqlite3
from applications.database_maintenance import (
    create_openstudio_standards_database_from_json,
)

conn = sqlite3.connect("openstudio_standards.db")
create_openstudio_standards_database_from_json(conn)
conn.close()
# %%
from applications.database_maintenance import (
    export_openstudio_standards_database_to_json,
)

conn = sqlite3.connect("openstudio_standards.db")
export_openstudio_standards_database_to_json(conn, save_dir="./database_files/")
# %%
