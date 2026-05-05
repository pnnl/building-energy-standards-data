import sqlite3
import pytest
import os

from tests.test_database import create_db

@pytest.fixture
def conn():
    db_name = "openstudio_standards"
    if not os.path.isfile(f"{db_name}.db"):
        conn = create_db(db_name=db_name, from_type="json")
    else:
        conn = sqlite3.connect(f"{db_name}.db")

    yield conn
    conn.close()