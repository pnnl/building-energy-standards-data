from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
cooling_type: TEXT
standard_model: TEXT
rating_condition: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
start_date: TEXT
end_date: TEXT
minimum_scop: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_COMPUTER_ROOM_AIR_CONDITIONERS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
cooling_type TEXT NOT NULL,
standard_model TEXT,
rating_condition TEXT,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
start_date TEXT,
end_date TEXT,
minimum_scop NUMERIC,
annotation TEXT);
"""

INSERT_A_COMPUTER_ROOM_AIR_CONDITIONERS_RECORD = """
    INSERT INTO %s (
template, 
cooling_type,
standard_model,
rating_condition,
minimum_capacity,
maximum_capacity,
start_date,
end_date,
minimum_scop,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "cooling_type": "",
    "standard_model": "",
    "rating_condition": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "start_date": "",
    "end_date": "",
    "minimum_scop": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementComputerRoomAirConditioners(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementComputerRoomAirConditioners, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_COMPUTER_ROOM_AIR_CONDITIONERS_TABLE
            % table_name,
            insert_record_query=INSERT_A_COMPUTER_ROOM_AIR_CONDITIONERS_RECORD
            % table_name,
        )

    def get_record_info(self):
        """
        A function to return the record info of the table
        :return:
        """
        return RECORD_HELP

    def validate_record_datatype(self, record):
        str_expected = [
            "template",
            "cooling_type",
            "standard_model",
            "rating_condition",
            "start_date",
            "end_date",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_scop",
        ]

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
            getattr_either("template", record),
            getattr_either("cooling_type", record),
            getattr_either("standard_model", record),
            getattr_either("rating_condition", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_scop", record),
            getattr_either("annotation", record),
        )
