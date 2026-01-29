from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
device: TEXT
adjustment_in_wc: NUMERIC
adjustment_in_wc_at_fan_system_design_conditions: TEXT
adjustment_in_wc_2_times_at_fan_system_design_conditions: TEXT
adjustment_in_wc_effectiveness_multiplier: NUMERIC
adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft: NUMERIC
annotation: TEXT (optional)
"""

CREATE_SYSTEM_requirements_fan_power_allowance_pressure_drop_adjustment_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
device TEXT,
adjustment_in_wc NUMERIC,
adjustment_in_wc_at_fan_system_design_conditions TEXT,
adjustment_in_wc_2_times_at_fan_system_design_conditions TEXT,
adjustment_in_wc_effectiveness_multiplier NUMERIC,
adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft NUMERIC,
annotation TEXT);
"""

INSERT_A_SYSTEM_requirements_fan_power_allowance_pressure_drop_adjustment_RECORD = """
    INSERT INTO %s (
template, 
device,
adjustment_in_wc,
adjustment_in_wc_at_fan_system_design_conditions,
adjustment_in_wc_2_times_at_fan_system_design_conditions,
adjustment_in_wc_effectiveness_multiplier,
adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "device": "",
    "adjustment_in_wc": 0.0,
    "adjustment_in_wc_at_fan_system_design_conditions": "",
    "adjustment_in_wc_2_times_at_fan_system_design_conditions": "",
    "adjustment_in_wc_effectiveness_multiplier": 0.0,
    "adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft": 0.0,
    "annotation": "",
}


class SystemRequirementsFanPowerAllowancePressureDropAdjustment(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(SystemRequirementsFanPowerAllowancePressureDropAdjustment, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_SYSTEM_requirements_fan_power_allowance_pressure_drop_adjustment_TABLE
            % table_name,
            insert_record_query=INSERT_A_SYSTEM_requirements_fan_power_allowance_pressure_drop_adjustment_RECORD
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
            "device" "adjustment_in_wc_at_fan_system_design_conditions",
            "adjustment_in_wc_2_times_at_fan_system_design_conditions",
        ]

        for f in str_expected:
            if record.get(f):
                assert isinstance(
                    record[f], str
                ), f"{f} requires to be a string, instead got {record[f]}"

        float_expected = [
            "adjustment_in_wc",
            "adjustment_in_wc_effectiveness_multiplier",
            "adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft",
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
            getattr_either("device", record),
            getattr_either("adjustment_in_wc", record),
            getattr_either("adjustment_in_wc_at_fan_system_design_conditions", record),
            getattr_either(
                "adjustment_in_wc_2_times_at_fan_system_design_conditions", record
            ),
            getattr_either("adjustment_in_wc_effectiveness_multiplier", record),
            getattr_either(
                "adjustment_in_wc_per_100_ft_of_verticaul_duct_exceeding_75_ft", record
            ),
            getattr_either("annotation", record),
        )
