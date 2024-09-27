from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

TABLE_NAME = "support_occupant_physical_characteristics"

RECORD_HELP = """
Must provide a dict that contains following key value pairs:
physical_characteristic_name TEXT UNIQUE NOT NULL PRIMARY KEY,
schedule_activity_level TEXT NOT NULL,
schedule_clothing_insulation TEXT NOT NULL,
schedule_air_velocity TEXT NOT NULL,
work_efficiency NUMERIC,
co2_generation NUMERIC,
co2_generation_units TEXT,
annotation TEXT,
"""

CREATE_PHYSICAL_CHAR_TABLE = """
CREATE TABLE IF NOT EXISTS support_occupant_physical_characteristics (
    physical_characteristic_name TEXT UNIQUE NOT NULL PRIMARY KEY ,
    schedule_activity_level TEXT NOT NULL,
    schedule_clothing_insulation TEXT NOT NULL,
    schedule_air_velocity TEXT NOT NULL,
    work_efficiency NUMERIC,
    co2_generation NUMERIC,
    co2_generation_units TEXT,
    annotation TEXT
);
"""

INSERT_PHYSICAL_CHAR = """
    INSERT INTO support_occupant_physical_characteristics
    (physical_characteristic_name,
    schedule_activity_level,
    schedule_clothing_insulation,
    schedule_air_velocity,
    work_efficiency,
    co2_generation,
    co2_generation_units,annotation)
    VALUES (?, ?, ?, ?, ?, ?, ?,?);
"""

RECORD_TEMPLATE = {
    "physical_characteristic_name": "",
    "schedule_activity_level": "",
    "schedule_clothing_insulation": "",
    "schedule_air_velocity": "",
    "work_efficiency": 0.0,
    "co2_generation": 0.0,
    "co2_generation_units": "",
    "annotation": "",
}


class SupportPhysicalCharacteristicsTable(DBOperation):
    def __init__(self):
        super(SupportPhysicalCharacteristicsTable, self).__init__(
            table_name=f"{TABLE_NAME}",
            record_template=RECORD_TEMPLATE,
            initial_data_directory=f"building_energy_standards_data/database_files/{TABLE_NAME}",
            create_table_query=CREATE_PHYSICAL_CHAR_TABLE,
            insert_record_query=INSERT_PHYSICAL_CHAR,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "physical_characteristic_name",
            "schedule_activity_level",
            "schedule_clothing_insulation",
            "schedule_air_velocity",
            "co2_generation_units",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = ["work_efficiency", "co2_generation"]

        for f in float_expected:
            if record.get(f):
                assert is_float(
                    record.get(f)
                ), f"{f} requires to be numeric data type, instead got {record[f]}"
        return True

    def _preprocess_record(self, record):
        """

        :param record: dict
        :return:
        """

        return (
            getattr_either("physical_characteristic_name", record),
            getattr_either("schedule_activity_level", record),
            getattr_either("schedule_clothing_insulation", record),
            getattr_either("schedule_air_velocity", record),
            getattr_either("work_efficiency", record),
            getattr_either("co2_generation", record),
            getattr_either("co2_generation_units", record),
            getattr_either("annotation", record),
        )
