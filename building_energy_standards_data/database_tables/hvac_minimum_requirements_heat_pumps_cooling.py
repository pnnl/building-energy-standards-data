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
heating_type: TEXT
subcategory: TEXT
application: TEXT
rating_condition: TEXT
electric_power_phase: NUMERIC
region: TEXT
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
start_date: TEXT
end_date: TEXT
minimum_seasonal_energy_efficiency_ratio: NUMERIC
minimum_seasonal_energy_efficiency_ratio_2: NUMERIC
minimum_energy_efficiency_ratio: NUMERIC
minimum_integrated_part_load_value: NUMERIC
minimum_integrated_energy_efficiency_ratio: NUMERIC
minimum_combined_energy_efficiency_ratio: NUMERIC
pthp_eer_coefficient_1: NUMERIC
pthp_eer_coefficient_2: NUMERIC
off_mode_power: NUMERIC
minimum_coefficient_of_performance_no_fan_cooling: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_heat_pumps_COOLING_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
equipment_type TEXT NOT NULL,
cooling_type TEXT NOT NULL,
heating_type TEXT,
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
minimum_seasonal_energy_efficiency_ratio NUMERIC,
minimum_seasonal_energy_efficiency_ratio_2 NUMERIC,
minimum_energy_efficiency_ratio NUMERIC,
minimum_integrated_part_load_value NUMERIC,
minimum_integrated_energy_efficiency_ratio NUMERIC,
minimum_combined_energy_efficiency_ratio NUMERIC,
pthp_eer_coefficient_1 NUMERIC,
pthp_eer_coefficient_2 NUMERIC,
off_mode_power NUMERIC,
minimum_coefficient_of_performance_no_fan_cooling NUMERIC,
annotation TEXT);
"""

INSERT_A_heat_pumps_COOLING_RECORD = """
    INSERT INTO %s (
template, 
equipment_type,
cooling_type,
heating_type,
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
minimum_seasonal_energy_efficiency_ratio,
minimum_seasonal_energy_efficiency_ratio_2,
minimum_energy_efficiency_ratio,
minimum_integrated_part_load_value,
minimum_integrated_energy_efficiency_ratio,
minimum_combined_energy_efficiency_ratio,
pthp_eer_coefficient_1,
pthp_eer_coefficient_2,
off_mode_power,
minimum_coefficient_of_performance_no_fan_cooling,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "cooling_type": "",
    "heating_type": "",
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
    "minimum_seasonal_energy_efficiency_ratio": 0.0,
    "minimum_seasonal_energy_efficiency_ratio_2": 0.0,
    "minimum_energy_efficiency_ratio": 0.0,
    "minimum_integrated_part_load_value": 0.0,
    "minimum_integrated_energy_efficiency_ratio": 0.0,
    "minimum_combined_energy_efficiency_ratio": 0.0,
    "pthp_eer_coefficient_1": 0.0,
    "pthp_eer_coefficient_2": 0.0,
    "off_mode_power": 0.0,
    "minimum_coefficient_of_performance_no_fan_cooling": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementHeatPumpCooling(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementHeatPumpCooling, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_heat_pumps_COOLING_TABLE
            % table_name,
            insert_record_query=INSERT_A_heat_pumps_COOLING_RECORD % table_name,
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
            "heating_type",
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
            "minimum_seasonal_energy_efficiency_ratio",
            "minimum_seasonal_energy_efficiency_ratio_2",
            "minimum_energy_efficiency_ratio",
            "minimum_integrated_part_load_value",
            "minimum_integrated_energy_efficiency_ratio",
            "minimum_combined_energy_efficiency_ratio",
            "pthp_eer_coefficient_1",
            "pthp_eer_coefficient_2",
            "off_mode_power",
            "minimum_coefficient_of_performance_no_fan_cooling",
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
            getattr_either("heating_type", record),
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
            getattr_either("minimum_seasonal_energy_efficiency_ratio", record),
            getattr_either("minimum_seasonal_energy_efficiency_ratio_2", record),
            getattr_either("minimum_energy_efficiency_ratio", record),
            getattr_either("minimum_integrated_part_load_value", record),
            getattr_either("minimum_integrated_energy_efficiency_ratio", record),
            getattr_either("minimum_combined_energy_efficiency_ratio", record),
            getattr_either("pthp_eer_coefficient_1", record),
            getattr_either("pthp_eer_coefficient_2", record),
            getattr_either("off_mode_power", record),
            getattr_either("minimum_coefficient_of_performance_no_fan_cooling", record),
            getattr_either("annotation", record),
        )
