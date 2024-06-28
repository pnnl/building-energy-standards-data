from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
cooling_type: TEXT
condenser_type: TEXT
compressor_type: TEXT
absorption_type: TEXT
compliance_path: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
start_date: TEXT
end_date: TEXT
minimum_coefficient_of_performance: NUMERIC
minimum_energy_efficiency_ratio: NUMERIC
minimum_kilowatts_per_tons: NUMERIC
minimum_integrated_part_load_value: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_CHILLERS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
cooling_type TEXT,
condenser_type TEXT,
compressor_type TEXT,
absorption_type TEXT,
compliance_path TEXT,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
start_date TEXT,
end_date TEXT,
minimum_coefficient_of_performance NUMERIC,
minimum_energy_efficiency_ratio NUMERIC,
minimum_kilowatts_per_tons NUMERIC,
minimum_integrated_part_load_value NUMERIC,
annotation TEXT);
"""

INSERT_A_CHILLER_RECORD = """
    INSERT INTO %s (
template, 
cooling_type,
condenser_type,
compressor_type,
absorption_type,
compliance_path,
minimum_capacity,
maximum_capacity,
start_date,
end_date,
minimum_coefficient_of_performance,
minimum_energy_efficiency_ratio,
minimum_kilowatts_per_tons,
minimum_integrated_part_load_value,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "cooling_type": "",
    "condenser_type": "",
    "compressor_type": "",
    "absorption_type": "",
    "compliance_path": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "start_date": "",
    "end_date": "",
    "minimum_coefficient_of_performance": 0.0,
    "minimum_energy_efficiency_ratio": 0.0,
    "minimum_kilowatts_per_tons": 0.0,
    "minimum_integrated_part_load_value": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementChillers(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementChillers, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_CHILLERS_TABLE % table_name,
            insert_record_query=INSERT_A_CHILLER_RECORD % table_name,
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
            "condenser_type",
            "compressor_type",
            "absorption_type",
            "compliance_path",
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
            "minimum_coefficient_of_performance",
            "minimum_energy_efficiency_ratio",
            "minimum_kilowatts_per_tons",
            "minimum_integrated_part_load_value",
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
            getattr_either("condenser_type", record),
            getattr_either("compressor_type", record),
            getattr_either("absorption_type", record),
            getattr_either("compliance_path", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_coefficient_of_performance", record),
            getattr_either("minimum_energy_efficiency_ratio", record),
            getattr_either("minimum_kilowatts_per_tons", record),
            getattr_either("minimum_integrated_part_load_value", record),
            getattr_either("annotation", record),
        )
