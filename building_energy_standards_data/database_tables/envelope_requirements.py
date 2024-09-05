from building_energy_standards_data.database_engine.assertions import assert_
from building_energy_standards_data.database_engine.database import DBOperation
from building_energy_standards_data.database_engine.database_util import (
    is_float,
    getattr_either,
)

RECORD_HELP = """
Must provide a tuple that contains:
template: TEXT
climate_zone_set: TEXT
intended_surface_type: TEXT
standards_construction_type: TEXT
building_category: TEXT
construction: TEXT
minimum_percent_of_surface: NUMERIC
maximum_percent_of_surface: NUMERIC
assembly_maximum_u_value: NUMERIC
assembly_maximum_u_value_unit: TEXT
u_value_includes_interior_film_coefficient: TEXT
u_value_includes_exterior_film_coefficient: TEXT
assembly_maximum_f_factor: NUMERIC
assembly_maximum_f_factor_unit: TEXT
assembly_maximum_c_factor: NUMERIC
assembly_maximum_c_factor_unit: TEXT
orientation: TEXT
minimum_projection_factor: NUMERIC
maximum_projection_factor: NUMERIC
assembly_maximum_solar_heat_gain_coefficient: NUMERIC
assembly_minimum_visible_transmittance: NUMERIC
assembly_minimum_vt_shgc: NUMERIC
annotation: TEXT (optional)
"""

CREATE_ENVELOPE_REQUIREMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS %s
(id INTEGER PRIMARY KEY, 
template TEXT NOT NULL, 
climate_zone_set TEXT NOT NULL,
intended_surface_type TEXT NOT NULL,
standards_construction_type TEXT,
building_category TEXT NOT NULL,
construction TEXT NOT NULL,
minimum_percent_of_surface NUMERIC,
maximum_percent_of_surface NUMERIC,
assembly_maximum_u_value NUMERIC,
assembly_maximum_u_value_unit TEXT,
u_value_includes_interior_film_coefficient TEXT,
u_value_includes_exterior_film_coefficient TEXT,
assembly_maximum_f_factor NUMERIC,
assembly_maximum_f_factor_unit TEXT,
assembly_maximum_c_factor NUMERIC,
assembly_maximum_c_factor_unit TEXT,
orientation TEXT,
minimum_projection_factor NUMERIC,
maximum_projection_factor NUMERIC,
assembly_maximum_solar_heat_gain_coefficient NUMERIC,
assembly_minimum_visible_transmittance NUMERIC,
assembly_minimum_vt_shgc NUMERIC,
annotation TEXT,
FOREIGN KEY(construction) REFERENCES support_constructions(name)
);
"""

INSERT_A_ENVELOPE_requirements_RECORD = """
    INSERT INTO %s (
template, 
climate_zone_set,
intended_surface_type,
standards_construction_type,
building_category,
construction,
minimum_percent_of_surface,
maximum_percent_of_surface,
assembly_maximum_u_value,
assembly_maximum_u_value_unit,
u_value_includes_interior_film_coefficient,
u_value_includes_exterior_film_coefficient,
assembly_maximum_f_factor,
assembly_maximum_f_factor_unit,
assembly_maximum_c_factor,
assembly_maximum_c_factor_unit,
orientation,
minimum_projection_factor,
maximum_projection_factor,
assembly_maximum_solar_heat_gain_coefficient,
assembly_minimum_visible_transmittance,
assembly_minimum_vt_shgc,
annotation
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

RECORD_TEMPLATE = {
    "template": "",
    "climate_zone_set": "",
    "intended_surface_type": "",
    "standards_construction_type": "",
    "building_category": "",
    "construction": "",
    "minimum_percent_of_surface": 0.0,
    "maximum_percent_of_surface": 0.0,
    "assembly_maximum_u_value": 0.0,
    "assembly_maximum_u_value_unit": "btu/h-ft2-F",
    "u_value_includes_interior_film_coefficient": 0.0,
    "u_value_includes_exterior_film_coefficient": 0.0,
    "assembly_maximum_f_factor": 0.0,
    "assembly_maximum_f_factor_unit": "btu/h-ft-F",
    "assembly_maximum_c_factor": 0.0,
    "assembly_maximum_c_factor_unit": "btu/h-ft2-F",
    "orientation": "",
    "minimum_projection_factor": 0.0,
    "maximum_projection_factor": 0.0,
    "assembly_maximum_solar_heat_gain_coefficient": 0.0,
    "assembly_minimum_visible_transmittance": 0.0,
    "assembly_minimum_vt_shgc": 0.0,
    "annotation": "",
}


class EnvelopeRequirement(DBOperation):
    def __init__(self, table_name, initial_data_directory):
        super(EnvelopeRequirement, self).__init__(
            table_name=table_name,
            record_template=RECORD_TEMPLATE,
            initial_data_directory=initial_data_directory,
            create_table_query=CREATE_ENVELOPE_REQUIREMENTS_TABLE % table_name,
            insert_record_query=INSERT_A_ENVELOPE_requirements_RECORD % table_name,
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
            "climate_zone_set",
            "intended_surface_type",
            "standards_construction_type",
            "building_category",
            "construction",
            "value_includes_interior_film_coefficient",
            "value_includes_exterior_film_coefficient",
            "orientation",
        ]

        for f in str_expected:
            if record.get(f):
                assert_(
                    isinstance(record[f], str),
                    f"{f} requires to be a string, instead got {record[f]}",
                )

        float_expected = [
            "minimum_percent_of_surface",
            "maximum_percent_of_surface",
            "assembly_maximum_u_value",
            "assembly_maximum_f_factor",
            "assembly_maximum_c_factor",
            "minimum_projection_factor",
            "maximum_projection_factor",
            "assembly_maximum_solar_heat_gain_coefficient",
            "assembly_minimum_visible_transmittance",
            "assembly_minimum_vt_shgc",
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
            getattr_either("climate_zone_set", record),
            getattr_either("intended_surface_type", record),
            getattr_either("standards_construction_type", record),
            getattr_either("building_category", record),
            getattr_either("construction", record),
            getattr_either("minimum_percent_of_surface", record),
            getattr_either("maximum_percent_of_surface", record),
            getattr_either("assembly_maximum_u_value", record),
            getattr_either("assembly_maximum_u_value_unit", record, "btu/h-ft2-F"),
            getattr_either("u_value_includes_interior_film_coefficient", record),
            getattr_either("u_value_includes_exterior_film_coefficient", record),
            getattr_either("assembly_maximum_f_factor", record),
            getattr_either("assembly_maximum_f_factor_unit", record, "btu/h-ft-F"),
            getattr_either("assembly_maximum_c_factor", record),
            getattr_either("assembly_maximum_c_factor_unit", record, "btu/h-ft2-F"),
            getattr_either("orientation", record),
            getattr_either("minimum_projection_factor", record),
            getattr_either("maximum_projection_factor", record),
            getattr_either("assembly_maximum_solar_heat_gain_coefficient", record),
            getattr_either("assembly_minimum_visible_transmittance", record),
            getattr_either("assembly_minimum_vt_shgc", record),
            getattr_either("annotation", record),
        )
