from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
operation: TEXT
climate_zone: TEXT
pump_head_ft: NUMERIC
VSD_pump_horsepower_threshold: NUMERIC
VSD_reset_pump_horsepower_threshold: NUMERIC
VSD_plant_W_threshold: NUMERIC
VSD_reset_plant_W_threshold: NUMERIC
VSD_building_area_served_threshold: NUMERIC
VSD_reset_building_area_served_threshold: NUMERIC
annotation: TEXT
"""

CREATE_SYSTEM_requirements_HYDRONIC_VARIABLE_FLOW_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
operation TEXT,
climate_zone TEXT,
pump_head_ft NUMERIC,
VSD_pump_horsepower_threshold NUMERIC,
VSD_reset_pump_horsepower_threshold NUMERIC,
VSD_plant_W_threshold NUMERIC,
VSD_reset_plant_W_threshold NUMERIC,
VSD_building_area_served_threshold NUMERIC,
VSD_reset_building_area_served_threshold NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_HYDRONIC_VARIABLE_FLOW_RECORD = """
    INSERT INTO %s (
template, 
operation,
climate_zone,
pump_head_ft,
VSD_pump_horsepower_threshold,
VSD_reset_pump_horsepower_threshold,
VSD_plant_W_threshold,
VSD_reset_plant_W_threshold,
VSD_building_area_served_threshold,
VSD_reset_building_area_served_threshold,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "operation": "",
    "climate_zone": "",
    "pump_head_ft": 0.0,
    "VSD_pump_horsepower_threshold": 0.0,
    "VSD_reset_pump_horsepower_threshold": 0.0,
    "VSD_plant_W_threshold": 0.0,
    "VSD_reset_plant_W_threshold": 0.0,
    "VSD_building_area_served_threshold": 0.0,
    "VSD_reset_building_area_served_threshold": 0.0,
    "annotation": "",
}


class SystemRequirementsHydronicVariableFlow(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementsHydronicVariableFlow, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_HYDRONIC_VARIABLE_FLOW_TABLE
            % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_HYDRONIC_VARIABLE_FLOW_RECORD
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
            "operation",
            "climate_zone",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "pump_head_ft",
            "VSD_pump_horsepower_threshold",
            "VSD_reset_pump_horsepower_threshold",
            "VSD_plant_W_threshold",
            "VSD_reset_plant_W_threshold",
            "VSD_building_area_served_threshold",
            "VSD_reset_building_area_served_threshold",
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
            getattr_either("operation", record),
            getattr_either("climate_zone", record),
            getattr_either("pump_head_ft", record),
            getattr_either("VSD_pump_horsepower_threshold", record),
            getattr_either("VSD_reset_pump_horsepower_threshold", record),
            getattr_either("VSD_plant_W_threshold", record),
            getattr_either("VSD_reset_plant_W_threshold", record),
            getattr_either("VSD_building_area_served_threshold", record),
            getattr_either("VSD_reset_building_area_served_threshold", record),
            getattr_either("annotation", record),
        )
