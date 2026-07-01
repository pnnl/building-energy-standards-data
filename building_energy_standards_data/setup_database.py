import sqlite3
from building_energy_standards_data.applications.database_maintenance import (
    create_openstudio_standards_database_from_json,
)


def setup_database():
    """
    Sets up the OpenStudio Standards database by creating it from JSON data.

    This function connects to the SQLite database file named 'openstudio_standards.db',
    creates the database structure and populates it with data from JSON files.
    After the setup is complete, the database connection is closed.

    Returns:
        None
    """
    conn = sqlite3.connect("openstudio_standards.db")
    create_openstudio_standards_database_from_json(conn)
    conn.close()


if __name__ == "__main__":
    setup_database()
