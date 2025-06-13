from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
equipment_type: TEXT
condensing_unit_configuration: TEXT
equipment_family: TEXT
equipment_classification: TEXT
rating_temp: NUMERIC
maximum_operating_temp: NUMERIC
minimum_operating_temp: NUMERIC
start_date: TEXT
end_date: TEXT
max_daily_energy_consumption_coeff1: NUMERIC
max_daily_energy_consumption_coeff2: NUMERIC
max_daily_energy_consumption_variable: TEXT
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_REFRIGERATORS_FREEZERS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL,
equipment_type TEXT,
condensing_unit_configuration TEXT NOT NULL,
equipment_family TEXT,
equipment_classification TEXT,
rating_temp NUMERIC,
maximum_operating_temp NUMERIC,
minimum_operating_temp NUMERIC,
start_date TEXT NOT NULL,
end_date TEXT NOT NULL,
max_daily_energy_consumption_coeff1 NUMERIC,
max_daily_energy_consumption_coeff2 NUMERIC,
max_daily_energy_consumption_variable TEXT,
annotation TEXT);
"""

INSERT_A_REFRIGERATORS_FREEZERS_RECORD = """
    INSERT INTO %s (
template,
equipment_type,
condensing_unit_configuration,
equipment_family,
equipment_classification,
rating_temp,
maximum_operating_temp,
minimum_operating_temp,
start_date,
end_date,
max_daily_energy_consumption_coeff1,
max_daily_energy_consumption_coeff2,
max_daily_energy_consumption_variable,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "condensing_unit_configuration": "",
    "equipment_family": "",
    "equipment_classification": "",
    "rating_temp": 0.0,
    "maximum_operating_temp": 0.0,
    "minimum_operating_temp": 0.0,
    "start_date": "",
    "end_date": "",
    "max_daily_energy_consumption_coeff1": 0.0,
    "max_daily_energy_consumption_coeff2": 0.0,
    "max_daily_energy_consumption_variable": "",
    "annotation": "",
}


class HVACMinimumRequirementRefrigeratorsFreezers(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementRefrigeratorsFreezers, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_REFRIGERATORS_FREEZERS_TABLE
            % table_name,
            insert_record_query=INSERT_A_REFRIGERATORS_FREEZERS_RECORD % table_name,
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
            "condensing_unit_configuration",
            "equipment_family",
            "equipment_classification",
            "start_date",
            "end_date",
            "max_daily_energy_consumption_variable",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "rating_temp",
            "maximum_operating_temp",
            "minimum_operating_temp",
            "max_daily_energy_consumption_coeff1",
            "max_daily_energy_consumption_coeff2",
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
            getattr_either("condensing_unit_configuration", record),
            getattr_either("equipment_family", record),
            getattr_either("equipment_classification", record),
            getattr_either("rating_temp", record),
            getattr_either("maximum_operating_temp", record),
            getattr_either("minimum_operating_temp", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("max_daily_energy_consumption_coeff1", record),
            getattr_either("max_daily_energy_consumption_coeff2", record),
            getattr_either("max_daily_energy_consumption_variable", record),
            getattr_either("annotation", record, ""),
        )
