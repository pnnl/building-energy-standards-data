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
minimum_capacity: NUMERIC
maximum_capacity: NUMERIC
minimum_storage: NUMERIC
maximum_storage: NUMERIC
minimum_capacity_per_storage: NUMERIC
maximum_capacity_per_storage: NUMERIC
draw profile: TEXT
start_date: TEXT
end_date: TEXT
energy_factor_base: NUMERIC
energy_factor_volume_derate: NUMERIC
standby_loss_base: NUMERIC
standby_loss_capacity_allowance: NUMERIC
standby_loss_volume_allowance: NUMERIC
standby_loss_square_root_volume_allowance: NUMERIC
hourly_loss_base: NUMERIC
hourly_loss_volume_allowance: NUMERIC
thermal_efficiency: NUMERIC
uniform_energy_factor: NUMERIC
uniform_energy_factor_base: NUMERIC
uniform_energy_factor_volume_allowance: NUMERIC
cop: NUMERIC
r_value: NUMERIC
first_hour_rating: NUMERIC
solar_energy_factor: NUMERIC
annotation: TEXT (optional)
"""

CREATE_HVAC_requirements_WATER_HEATERS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL,
equipment_type TEXT,
fuel_type TEXT NOT NULL,
minimum_capacity NUMERIC,
maximum_capacity NUMERIC,
minimum_storage NUMERIC,
maximum_storage NUMERIC,
minimum_capacity_per_storage NUMERIC,
maximum_capacity_per_storage NUMERIC,
draw_profile TEXT,
start_date TEXT NOT NULL,
end_date TEXT NOT NULL,
energy_factor_base NUMERIC,
energy_factor_volume_derate NUMERIC,
standby_loss_base NUMERIC,
standby_loss_capacity_allowance NUMERIC,
standby_loss_volume_allowance NUMERIC,
standby_loss_square_root_volume_allowance NUMERIC,
hourly_loss_base NUMERIC,
hourly_loss_volume_allowance NUMERIC,
thermal_efficiency NUMERIC,
uniform_energy_factor NUMERIC,
uniform_energy_factor_base NUMERIC,
uniform_energy_factor_volume_allowance NUMERIC,
cop NUMERIC,
r_value NUMERIC,
first_hour_rating NUMERIC,
solar_energy_factor NUMERIC,
annotation TEXT);
"""

INSERT_A_WATER_HEATER_RECORD = """
    INSERT INTO %s (
template,
equipment_type,
fuel_type,
minimum_capacity,
maximum_capacity,
minimum_storage,
maximum_storage,
minimum_capacity_per_storage,
maximum_capacity_per_storage,
draw_profile,
start_date,
end_date,
energy_factor_base,
energy_factor_volume_derate,
standby_loss_base,
standby_loss_capacity_allowance,
standby_loss_volume_allowance,
standby_loss_square_root_volume_allowance,
hourly_loss_base,
hourly_loss_volume_allowance,
thermal_efficiency,
uniform_energy_factor,
uniform_energy_factor_base,
uniform_energy_factor_volume_allowance,
cop,
r_value,
first_hour_rating,
solar_energy_factor,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "equipment_type": "",
    "fuel_type": "",
    "minimum_capacity": 0.0,
    "maximum_capacity": 0.0,
    "minimum_storage": 0.0,
    "maximum_storage": 0.0,
    "minimum_capacity_per_storage": 0.0,
    "maximum_capacity_per_storage": 0.0,
    "draw_profile": "",
    "start_date": "",
    "end_date": "",
    "energy_factor_base": 0.0,
    "energy_factor_volume_derate": 0.0,
    "standby_loss_base": 0.0,
    "standby_loss_capacity_allowance": 0.0,
    "standby_loss_volume_allowance": 0.0,
    "standby_loss_square_root_volume_allowance": 0.0,
    "hourly_loss_base": 0.0,
    "hourly_loss_volume_allowance": 0.0,
    "thermal_efficiency": 0.0,
    "uniform_energy_factor": 0.0,
    "uniform_energy_factor_base": 0.0,
    "uniform_energy_factor_volume_allowance": 0.0,
    "cop": 0.0,
    "r_value": 0.0,
    "first_hour_rating": 0.0,
    "solar_energy_factor": 0.0,
    "annotation": "",
}


class HVACMinimumRequirementWaterHeaters(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(HVACMinimumRequirementWaterHeaters, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_HVAC_requirements_WATER_HEATERS_TABLE
            % table_name,
            insert_record_query=INSERT_A_WATER_HEATER_RECORD % table_name,
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
            "fuel_type",
            "start_date",
            "end_date",
            "equipment_type",
            "draw_profile",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "minimum_capacity",
            "maximum_capacity",
            "minimum_storage",
            "maximum_storage",
            "minimum_capacity_per_storage",
            "maximum_capacity_per_storage",
            "energy_factor_base",
            "energy_factor_volume_derate",
            "standby_loss_base",
            "standby_loss_capacity_allowance",
            "standby_loss_volume_allowance",
            "standby_loss_square_root_volume_allowance",
            "hourly_loss_base",
            "hourly_loss_volume_allowance",
            "thermal_efficiency",
            "uniform_energy_factor",
            "uniform_energy_factor_base",
            "uniform_energy_factor_volume_allowance",
            "cop",
            "r_value",
            "first_hour_rating",
            "solar_energy_factor",
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
            getattr_either("minimum_capacity", record),
            getattr_either("maximum_capacity", record),
            getattr_either("minimum_storage", record),
            getattr_either("maximum_storage", record),
            getattr_either("minimum_capacity_per_storage", record),
            getattr_either("maximum_capacity_per_storage", record),
            getattr_either("draw_profile", record),
            getattr_either("start_date", record),
            getattr_either("end_date", record),
            getattr_either("energy_factor_base", record),
            getattr_either("energy_factor_volume_derate", record),
            getattr_either("standby_loss_base", record),
            getattr_either("standby_loss_capacity_allowance", record),
            getattr_either("standby_loss_volume_allowance", record),
            getattr_either("standby_loss_square_root_volume_allowance", record),
            getattr_either("hourly_loss_base", record),
            getattr_either("hourly_loss_volume_allowance", record),
            getattr_either("thermal_efficiency", record),
            getattr_either("uniform_energy_factor", record),
            getattr_either("uniform_energy_factor_base", record),
            getattr_either("uniform_energy_factor_volume_allowance", record),
            getattr_either("cop", record),
            getattr_either("r_value", record),
            getattr_either("first_hour_rating", record),
            getattr_either("solar_energy_factor", record),
            getattr_either("annotation", record),
        )
