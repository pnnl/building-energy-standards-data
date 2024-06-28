from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
equipment_type: TEXT
fuel_type: TEXT
electric_power_phase: NUMERIC
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
minimum_combo_unit_cooling_capacity: NUMERIC
maximum_combo_unit_cooling_capacity: NUMERIC
subtype: TEXT
start_date: TEXT
end_date: TEXT
minimum_annual_fuel_utilization_efficiency: NUMERIC
minimum_thermal_efficiency: NUMERIC
minimum_combustion_efficiency: NUMERIC
standby_mode_power: NUMERIC
off_mode_power: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_FURNACES_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL,
equipment_type TEXT NOT NULL,
fuel_type TEXT NOT NULL,
electric_power_phase NUMERIC,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
minimum_combo_unit_cooling_capacity NUMERIC,
maximum_combo_unit_cooling_capacity NUMERIC,
subtype TEXT,
start_date TEXT NOT NULL,
end_date TEXT NOT NULL,
minimum_annual_fuel_utilization_efficiency NUMERIC,
minimum_thermal_efficiency NUMERIC,
minimum_combustion_efficiency NUMERIC,
standby_mode_power NUMERIC,
off_mode_power NUMERIC,
annotation TEXT);
"""

INSERT_A_FURNACE_RECORD = """
    INSERT INTO %s (
template,
equipment_type,
fuel_type,
electric_power_phase,
minimum_capacity,
maximum_capacity,
minimum_combo_unit_cooling_capacity,
maximum_combo_unit_cooling_capacity,
subtype,
start_date,
end_date,
minimum_annual_fuel_utilization_efficiency,
minimum_thermal_efficiency,
minimum_combustion_efficiency,
standby_mode_power,
off_mode_power,
annotation
) 
VALUES (?, ?, ?, ? ,? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "fuel_type": "",
    "electric_power_phase": 0.0,
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "minimum_combo_unit_cooling_capacity": 0.0,
    "maximum_combo_unit_cooling_capacity": 0.0,
    "subtype": "",
    "start_date": "",
    "end_date": "",
    "minimum_annual_fuel_utilization_efficiency": 0.0,
    "minimum_thermal_efficiency": 0.0,
    "minimum_combustion_efficiency": 0.0,
    "standby_mode_power": 0.0,
    "off_mode_power": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementFurnaces(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementFurnaces, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_FURNACES_TABLE % table_name,
            insert_record_query=INSERT_A_FURNACE_RECORD % table_name,
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
            "fuel_type",
            "subtype",
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
            "minimum_combo_unit_cooling_capacity",
            "maximum_combo_unit_cooling_capacity",
            "minimum_annual_fuel_utilization_efficiency",
            "minimum_thermal_efficiency",
            "minimum_combustion_efficiency",
            "standby_mode_power",
            "off_mode_power",
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
            getattr_either("fuel_type", record),
            getattr_either("electric_power_phase", record),
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("minimum_combo_unit_cooling_capacity", record),
            getattr_either("maximum_combo_unit_cooling_capacity", record),
            getattr_either("subtype", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("minimum_annual_fuel_utilization_efficiency", record),
            getattr_either("minimum_thermal_efficiency", record),
            getattr_either("minimum_combustion_efficiency", record),
            getattr_either("standby_mode_power", record),
            getattr_either("off_mode_power", record),
            getattr_either("annotation", record),
        )
