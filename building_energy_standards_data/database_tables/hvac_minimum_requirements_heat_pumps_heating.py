from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
equipment_type: TEXT
cooling_type: TEXT
configuration: TEXT
subcategory: TEXT
application: TEXT
rating_condition: TEXT
electric_power_phase: NUMERIC
region: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
start_date: TEXT
end_date: TEXT
minimum_heating_seasonal_performance_factor: NUMERIC
minimum_heating_seasonal_performance_factor_2: NUMERIC
minimum_coefficient_of_performance_heating: NUMERIC
pthp_cop_coefficient_1: NUMERIC
pthp_cop_coefficient_2: NUMERIC
off_mode_power: NUMERIC
minimum_coefficient_of_performance_no_fan_heating: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_heat_pumps_HEATING_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
equipment_type TEXT NOT NULL,
cooling_type TEXT NOT NULL,
configuration TEXT,
subcategory TEXT,
application TEXT,
rating_condition TEXT,
electric_power_phase NUMERIC,
region TEXT,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
start_date TEXT,
end_date TEXT,
minimum_heating_seasonal_performance_factor NUMERIC,
minimum_heating_seasonal_performance_factor_2 NUMERIC,
minimum_coefficient_of_performance_heating NUMERIC,
pthp_cop_coefficient_1 NUMERIC,
pthp_cop_coefficient_2 NUMERIC,
off_mode_power NUMERIC,
minimum_coefficient_of_performance_no_fan_heating NUMERIC,
annotation TEXT);
"""

INSERT_A_heat_pumps_HEATING_RECORD = """
    INSERT INTO %s (
template, 
equipment_type,
cooling_type,
configuration,
subcategory,
application,
rating_condition,
electric_power_phase,
region,
minimum_capacity,
maximum_capacity,
start_date,
end_date,
minimum_heating_seasonal_performance_factor,
minimum_heating_seasonal_performance_factor_2,
minimum_coefficient_of_performance_heating,
pthp_cop_coefficient_1,
pthp_cop_coefficient_2,
off_mode_power,
minimum_coefficient_of_performance_no_fan_heating,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "cooling_type": "",
    "configuration": "",
    "subcategory": "",
    "application": "",
    "rating_condition": "",
    "electric_power_phase": 0.0,
    "region": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "start_date": "",
    "end_date": "",
    "minimum_heating_seasonal_performance_factor": 0.0,
    "minimum_heating_seasonal_performance_factor_2": 0.0,
    "minimum_coefficient_of_performance_heating": 0.0,
    "pthp_cop_coefficient_1": 0.0,
    "pthp_cop_coefficient_2": 0.0,
    "off_mode_power": 0.0,
    "minimum_coefficient_of_performance_no_fan_heating": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementHeatPumpHeating(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementHeatPumpHeating, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_heat_pumps_HEATING_TABLE
            % table_name,
            insert_record_query=INSERT_A_heat_pumps_HEATING_RECORD % table_name,
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
            "cooling_type",
            "configuration",
            "subcategory",
            "application",
            "rating_condition",
            "region",
            "start_date",
            "end_date",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "electric_power_phase",
            "minimum_capacity",
            "maximum_capacity",
            "minimum_heating_seasonal_performance_factor",
            "minimum_heating_seasonal_performance_factor_2",
            "minimum_coefficient_of_performance_heating",
            "pthp_cop_coefficient_1",
            "pthp_cop_coefficient_2",
            "off_mode_power",
            "minimum_coefficient_of_performance_no_fan_heating",
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
            getattr_either("cooling_type", record),
            getattr_either("configuration", record),
            getattr_either("subcategory", record),
            getattr_either("application", record),
            getattr_either("rating_condition", record),
            getattr_either("electric_power_phase", record),
            getattr_either("region", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_heating_seasonal_performance_factor", record),
            getattr_either("minimum_heating_seasonal_performance_factor_2", record),
            getattr_either("minimum_coefficient_of_performance_heating", record),
            getattr_either("pthp_cop_coefficient_1", record),
            getattr_either("pthp_cop_coefficient_2", record),
            getattr_either("off_mode_power", record),
            getattr_either("minimum_coefficient_of_performance_no_fan_heating", record),
            getattr_either("annotation", record),
        )
