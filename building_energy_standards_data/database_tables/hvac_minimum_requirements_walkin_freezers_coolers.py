from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
equipment_type: TEXT
class: TEXT
minimum_capacity: TEXT
maximum_capacity: TEXT
start_date: TEXT
end_date: TEXT
minimum_awef_value: NUMERIC
minimum_awef_coeff1: NUMERIC
minimum_awef_coeff2: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_WALKIN_FREEZERS_COOLERS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL,
equipment_type TEXT,
class TEXT NOT NULL,
minimum_capacity TEXT,
maximum_capacity TEXT,
start_date TEXT NOT NULL,
end_date TEXT NOT NULL,
minimum_awef_value NUMERIC,
minimum_awef_coeff1 NUMERIC,
minimum_awef_coeff2 TEXT,
annotation TEXT);
"""

INSERT_A_WALKIN_FREEZERS_COOLERS_RECORD = """
    INSERT INTO %s (
template,
equipment_type,
class,
minimum_capacity,
maximum_capacity,
start_date,
end_date,
minimum_awef_value,
minimum_awef_coeff1,
minimum_awef_coeff2,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "class": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "start_date": "",
    "end_date": "",
    "minimum_awef_value": 0.0,
    "minimum_awef_coeff1": 0.0,
    "minimum_awef_coeff2": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementWalkinFreezersCoolers(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementWalkinFreezersCoolers, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_WALKIN_FREEZERS_COOLERS_TABLE
            % table_name,
            insert_record_query=INSERT_A_WALKIN_FREEZERS_COOLERS_RECORD % table_name,
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
            "equipment_type",
            "class",
            "start_date",
            "end_date",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_capacity",
            "maximum_capacity",
            "minimum_awef_value",
            "minimum_awef_coeff1",
            "minimum_awef_coeff2",
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
            getattr_either("equipment_type", record),
            getattr_either("class", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_awef_value", record),
            getattr_either("minimum_awef_coeff1", record),
            getattr_either("minimum_awef_coeff2", record),
            getattr_either("annotation", record, ""),
        )
