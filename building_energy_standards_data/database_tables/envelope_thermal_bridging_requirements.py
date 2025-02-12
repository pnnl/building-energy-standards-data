from building_energy_standards_data.database_engine.assertions import assert_
from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
class_of_construction: TEXT
thermal_bridge_type: TEXT
mitigated_psi_factor: NUMERIC
unmitigated_psi_factor: NUMERIC
mitigated_chi_factor: NUMERIC
unmitigated_chi_factor: NUMERIC
psi_factor_unit: TEXT
chi_factor_unit: TEXT
annotation: TEXT (optional)
"""

CREATE_ENVELOPE_THERMAL_BRIDGING_REQUIREMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL,
class_of_construction TEXT, 
thermal_bridge_type TEXT,
mitigated_psi_factor NUMERIC,
unmitigated_psi_factor NUMERIC,
mitigated_chi_factor NUMERIC,
unmitigated_chi_factor NUMERIC,
psi_factor_unit TEXT,
chi_factor_unit TEXT,
annotation TEXT
);
"""

INSERT_A_ENVELOPE_THERMAL_BRIDGING_requirements_RECORD = """
    INSERT INTO %s (
template,
class_of_construction,
thermal_bridge_type,
mitigated_psi_factor,
unmitigated_psi_factor,
mitigated_chi_factor,
unmitigated_chi_factor,
psi_factor_unit,
chi_factor_unit,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "class_of_construction": "",
    "thermal_bridge_type": "",
    "mitigated_psi_factor": 0.0,
    "unmitigated_psi_factor": 0.0,
    "mitigated_chi_factor": 0.0,
    "unmitigated_chi_factor": 0.0,
    "psi_factor_unit": "Btu/h.ft.F",
    "chi_factor_unit": "Btu/h.F",
    "annotation": "",
}


class EnvelopeThermalBridgingRequirement(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(EnvelopeThermalBridgingRequirement, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_ENVELOPE_THERMAL_BRIDGING_REQUIREMENTS_TABLE
            % table_name,
            insert_record_query=INSERT_A_ENVELOPE_THERMAL_BRIDGING_requirements_RECORD
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
            "class_of_construction",
            "template",
            "thermal_bridge_type" "psi_factor_unit",
            "chi_factor_unit",
        ]

        for f in str_expected:
            if record.get(f):
                assert_(
                    isinstance(record[f], str),
                    f"{f} requires to be a string, instead got {record[f]}",
                )

        float_expected = [
            "mitigated_psi_factor",
            "unmitigated_psi_factor",
            "mitigated_chi_factor",
            "unmitigated_chi_factor",
        ]

        for f in float_expected:
            if record.get(f):
                assert_(
                    is_float(record.get(f)),
                    f"{f} requires to be numeric data type, instead got {record[f]}",
                )
        return True

    def _preprocess_record(self, record):
        """

        :param record: dict
        :return:
        """

        return (
            getattr_either("template", record),
            getattr_either("class_of_construction", record),
            getattr_either("thermal_bridge_type", record),
            getattr_either("mitigated_psi_factor", record),
            getattr_either("unmitigated_psi_factor", record),
            getattr_either("mitigated_chi_factor", record),
            getattr_either("unmitigated_chi_factor", record),
            getattr_either("psi_factor_unit", record),
            getattr_either("chi_factor_unit", record),
            getattr_either("annotation", record),
        )
