import importlib
import inspect

import building_energy_standards_data.database_engine.database as database_classes
import building_energy_standards_data.database_tables as db_tables

# need to be in orders of complexity
# Tables with no foreign key need to be created
# before other tables
__all__ = [
    # tables no foreign keys
    "hvac_minimum_requirements_motors_90_1",
    "hvac_minimum_requirements_motors_90_1_prm",
    "hvac_minimum_requirements_motors_IECC",
    "hvac_minimum_requirements_motors_189_1",
    "hvac_minimum_requirements_water_heaters_90_1",
    "hvac_minimum_requirements_water_heaters_90_1_prm",
    "hvac_minimum_requirements_water_heaters_IECC",
    "hvac_minimum_requirements_water_heaters_189_1",
    "hvac_minimum_requirements_heat_rejection_90_1",
    "hvac_minimum_requirements_heat_rejection_IECC",
    "hvac_minimum_requirements_heat_rejection_90_1_prm",
    "hvac_minimum_requirements_heat_rejection_189_1",
    "hvac_minimum_requirements_unitary_air_conditioners_90_1",
    "hvac_minimum_requirements_unitary_air_conditioners_90_1_prm",
    "hvac_minimum_requirements_unitary_air_conditioners_IECC",
    "hvac_minimum_requirements_unitary_air_conditioners_189_1",
    "hvac_minimum_requirements_heat_pumps_cooling_90_1",
    "hvac_minimum_requirements_heat_pumps_cooling_90_1_prm",
    "hvac_minimum_requirements_heat_pumps_cooling_IECC",
    "hvac_minimum_requirements_heat_pumps_cooling_189_1",
    "hvac_minimum_requirements_heat_pumps_heating_90_1",
    "hvac_minimum_requirements_heat_pumps_heating_90_1_prm",
    "hvac_minimum_requirements_heat_pumps_heating_IECC",
    "hvac_minimum_requirements_heat_pumps_heating_189_1",
    "hvac_minimum_requirements_chillers_90_1",
    "hvac_minimum_requirements_chillers_90_1_prm",
    "hvac_minimum_requirements_chillers_IECC",
    "hvac_minimum_requirements_chillers_189_1",
    "hvac_minimum_requirements_boilers_90_1",
    "hvac_minimum_requirements_boilers_90_1_prm",
    "hvac_minimum_requirements_boilers_IECC",
    "hvac_minimum_requirements_boilers_189_1",
    "hvac_minimum_requirements_furnaces_90_1",
    "hvac_minimum_requirements_furnaces_90_1_prm",
    "hvac_minimum_requirements_furnaces_IECC",
    "hvac_minimum_requirements_furnaces_189_1",
    "level_3_lighting_90_1_2022",
    "level_3_lighting_90_1_2019",
    "level_3_lighting_90_1_2016",
    "level_3_lighting_90_1_2013",
    "level_3_lighting_90_1_2010",
    "level_3_lighting_90_1_2007",
    "level_3_lighting_90_1_2004",
    "level_3_lighting_90_1_2022_prm",
    "level_3_lighting_90_1_2019_prm",
    "level_3_lighting_90_1_2016_prm",
    "level_3_lighting_90_1_2013_prm",
    "level_3_lighting_90_1_2010_prm",
    "level_3_lighting_90_1_2007_prm",
    "level_3_lighting_90_1_2004_prm",
    "level_3_lighting_IECC_2021",
    "level_3_lighting_IECC_2018",
    "level_3_lighting_IECC_2015",
    "level_3_lighting_IECC_2012",
    "level_3_lighting_IECC_2009",
    "level_3_lighting_IECC_2006",
    "level_3_ventilation_62_1_2022",
    "level_3_ventilation_62_1_2019",
    "level_3_ventilation_62_1_2016",
    "level_3_ventilation_62_1_2013",
    "level_3_ventilation_62_1_2010",
    "level_3_ventilation_62_1_2007",
    "level_3_ventilation_62_1_2004",
    "level_3_ventilation_62_1_1999",
    "level_2_electric_equipment",
    "level_2_natural_gas_equipment",
    "support_lighting_technologies",
    "support_standard_templates",
    "support_lighting_space_type_name_tags",
    "support_ventilation_space_type_name_tags",
    "support_electric_equipment_space_type_name_tags",
    "support_materials",
    "support_performance_curves",
    "support_schedules",
    "system_requirements_energy_recovery_90_1",
    "system_requirements_energy_recovery_IECC",
    "system_requirements_energy_recovery_90_1_prm",
    "system_requirements_air_economizer_90_1",
    "system_requirements_air_economizer_90_1_prm",
    "system_requirements_air_economizer_IECC",
    "hvac_minimum_requirements_computer_room_air_conditioners_90_1",
    "hvac_minimum_requirements_computer_room_air_conditioners_IECC",
    "hvac_minimum_requirements_computer_room_air_conditioners_189_1",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_90_1",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_IECC",
    "hvac_minimum_requirements_variable_refrigerant_flow_systems_189_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_90_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_90_1_prm",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_189_1",
    "hvac_minimum_requirements_commercial_refrigerators_freezers_IECC",
    "hvac_minimum_requirements_walkin_freezers_coolers_90_1",
    "hvac_minimum_requirements_walkin_freezers_coolers_90_1_prm",
    "hvac_minimum_requirements_walkin_freezers_coolers_189_1",
    "hvac_minimum_requirements_walkin_freezers_coolers_IECC",
    "exterior_lighting_90_1",
    "exterior_lighting_90_1_prm",
    "exterior_lighting_IECC",
    "support_occupant_energy_behavior",
    "support_occupant_physical_characteristics",
    "envelope_thermal_bridging_requirements_IECC",
    "envelope_thermal_bridging_requirements_90_1",
    "system_requirements_fan_power_allowance_90_1",
    # tables with foreign keys
    "level_2_lighting_space_types",
    "level_2_ventilation_space_types",
    "level_1_space_types",
    "support_constructions",
    "envelope_requirements_90_1",
    "envelope_requirements_90_1_prm",
    "envelope_requirements_IECC",
    "support_occupant_types",
]


def __get_light_tables__():
    available_tables = __gettables__()
    return [table for table in available_tables if table[0].startswith("LightDef")]


def __gettables__():
    tables = inspect.getmembers(db_tables, inspect.ismodule)
    # sort the list tuples to the same order as __all__
    tables_sorted = [
        table for table_name in __all__ for table in tables if table_name == table[0]
    ]
    base_class_names = [
        f[0] for f in inspect.getmembers(database_classes, inspect.isclass)
    ]
    available_tables = []
    for table in tables_sorted:
        available_tables += [
            f
            for f in inspect.getmembers(
                table[1],
                lambda obj: inspect.isclass(obj)
                and issubclass(obj, database_classes.DBOperation),
            )
            if (not f[0].startswith("_"))
            and (not f[0] in base_class_names)
            and (f[0].endswith("Table"))
        ]

    return available_tables


def __getattr__(name):
    if name in __all__:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return __all__
