import sqlite3

from building_energy_standards_data.applications.database_maintenance import export_openstudio_standards_database_to_csv
conn = sqlite3.connect('openstudio_standards.db')
export_openstudio_standards_database_to_csv(conn, save_dir='./building_energy_standards_data/database_files/')