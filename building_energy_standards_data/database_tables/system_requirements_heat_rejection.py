from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
maximum_gpm_for_open_centrifugal_tower: NUMERIC
reference_condenser_water_return_deg_F: NUMERIC
reference_condenser_water_supply_deg_F: NUMERIC
reference_outdoor_air_wet_bulb_temperature_deg_F: NUMERIC
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_heat_rejection_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
maximum_gpm_for_open_centrifugal_tower NUMERIC,
reference_condenser_water_return_deg_F NUMERIC,
reference_condenser_water_supply_deg_F NUMERIC,
reference_outdoor_air_wet_bulb_temperature_deg_F NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_heat_rejection_RECORD = """
    INSERT INTO %s (
template, 
maximum_gpm_for_open_centrifugal_tower,
reference_condenser_water_return_deg_F,
reference_condenser_water_supply_deg_F,
reference_outdoor_air_wet_bulb_temperature_deg_F,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "maximum_gpm_for_open_centrifugal_tower": 0.0,
    "reference_condenser_water_return_deg_F": 0.0,
    "reference_condenser_water_supply_deg_F": 0.0,
    "reference_outdoor_air_wet_bulb_temperature_deg_F": 0.0,
    "annotation": "",
}


class SystemRequirementsHeatRejection(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementsHeatRejection, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_heat_rejection_TABLE % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_heat_rejection_RECORD % table_name,
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
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "maximum_gpm_for_open_centrifugal_tower",
            "reference_condenser_water_return_deg_F",
            "reference_condenser_water_supply_deg_F",
            "reference_outdoor_air_wet_bulb_temperature_deg_F",
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
            getattr_either("maximum_gpm_for_open_centrifugal_tower", record),
            getattr_either("reference_condenser_water_return_deg_F", record),
            getattr_either("reference_condenser_water_supply_deg_F", record),
            getattr_either("reference_outdoor_air_wet_bulb_temperature_deg_F", record),
            getattr_either("annotation", record),
        )
