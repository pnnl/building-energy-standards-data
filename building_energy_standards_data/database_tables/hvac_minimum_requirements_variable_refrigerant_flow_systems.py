from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
equipment_type: TEXT
heating_type: TEXT
subcategory: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
start_date: TEXT
end_date: TEXT
minimum_seasonal_energy_efficiency_ratio: NUMERIC
minimum_seasonal_energy_efficiency_ratio_2: NUMERIC
minimum_energy_efficiency_ratio: NUMERIC
minimum_energy_efficiency_ratio_2: NUMERIC
minimum_integrated_part_load_value: NUMERIC
minimum_heating_seasonal_performance_factor: NUMERIC
minimum_heating_seasonal_performance_factor_2: NUMERIC
minimum_coefficient_of_performance_heating: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_VRF_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
equipment_type TEXT NOT NULL,
heating_type TEXT,
subcategory TEXT,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
start_date TEXT,
end_date TEXT,
minimum_seasonal_energy_efficiency_ratio NUMERIC,
minimum_seasonal_energy_efficiency_ratio_2 NUMERIC,
minimum_energy_efficiency_ratio NUMERIC,
minimum_energy_efficiency_ratio_2 NUMERIC,
minimum_integrated_part_load_value NUMERIC,
minimum_heating_seasonal_performance_factor NUMERIC,
minimum_heating_seasonal_performance_factor_2 NUMERIC,
minimum_coefficient_of_performance_heating NUMERIC,
annotation TEXT);
"""

INSERT_A_VRF_RECORD = """
    INSERT INTO %s (
template, 
equipment_type,
heating_type,
subcategory,
minimum_capacity,
maximum_capacity,
start_date,
end_date,
minimum_seasonal_energy_efficiency_ratio,
minimum_seasonal_energy_efficiency_ratio_2,
minimum_energy_efficiency_ratio,
minimum_energy_efficiency_ratio_2,
minimum_integrated_part_load_value,
minimum_heating_seasonal_performance_factor,
minimum_heating_seasonal_performance_factor_2,
minimum_coefficient_of_performance_heating,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "heating_type": "",
    "subcategory": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "start_date": "",
    "end_date": "",
    "minimum_seasonal_energy_efficiency_ratio": 0.0,
    "minimum_seasonal_energy_efficiency_ratio_2": 0.0,
    "minimum_energy_efficiency_ratio": 0.0,
    "minimum_energy_efficiency_ratio_2": 0.0,
    "minimum_integrated_part_load_value": 0.0,
    "minimum_heating_seasonal_performance_factor": 0.0,
    "minimum_heating_seasonal_performance_factor_2": 0.0,
    "minimum_coefficient_of_performance_heating": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementVRF(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementVRF, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_VRF_TABLE % table_name,
            insert_record_query=INSERT_A_VRF_RECORD % table_name,
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
            "heating_type",
            "subcategory",
            "start_date",
            "end_date",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_seasonal_energy_efficiency_ratio",
            "minimum_seasonal_energy_efficiency_ratio_2",
            "minimum_energy_efficiency_ratio",
            "minimum_energy_efficiency_ratio_2",
            "minimum_integrated_part_load_value",
            "minimum_heating_seasonal_performance_factor",
            "minimum_heating_seasonal_performance_factor_2",
            "minimum_coefficient_of_performance_heating",
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
            getattr_either("heating_type", record),
            getattr_either("subcategory", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_seasonal_energy_efficiency_ratio", record),
            getattr_either("minimum_seasonal_energy_efficiency_ratio_2", record),
            getattr_either("minimum_energy_efficiency_ratio", record),
            getattr_either("minimum_energy_efficiency_ratio_2", record),
            getattr_either("minimum_integrated_part_load_value", record),
            getattr_either("minimum_heating_seasonal_performance_factor", record),
            getattr_either("minimum_heating_seasonal_performance_factor_2", record),
            getattr_either("minimum_coefficient_of_performance_heating", record),
            getattr_either("annotation", record),
        )
