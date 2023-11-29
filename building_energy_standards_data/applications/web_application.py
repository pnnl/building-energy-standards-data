from building_energy_standards_data.database_engine.database import create_connect
from building_energy_standards_data.query.fetch.database_table import (
    fetch_records_from_table_by_key_values,
    fetch_table,
    fetch_a_record_from_table_by_id,
    fetch_columns_from_table,
)
from building_energy_standards_data.applications import web_application_helpers as helpers


def get_space_types(database_path: str | None = None):
    conn = create_connect(database_path)

    space_type_dicts = fetch_columns_from_table(
        conn, "level_1_space_types", "space_type_name"
    )
    space_type_list = [entry["space_type_name"] for entry in space_type_dicts]
    return space_type_list


def get_subspace_types(
    space_type: str,
    subspace_type: str | None = None,
    template: str | None = None,
    database_path: str | None = None,
):
    conn = create_connect(database_path)

    # allow users to substitute _ for whitespace
    space_type = space_type.replace("_", " ")
    space_type = space_type.replace("-", "/")

    # select 1 record
    space_info_list = fetch_records_from_table_by_key_values(
        conn, "level_1_space_types", key_value_dict={"space_type_name": space_type}
    )

    # get record from space_info_list if space_info_list exists. If not, space_type is likely a natural_gas_equipment_space_type
    if space_info_list:
        assert len(space_info_list) == 1
        space_info = space_info_list[0]
    else:
        return

    if subspace_type:
        # client wants a single sub space type for given space type
        subspace_type_info = get_subspace_type_info(
            subspace_type, space_type, conn, space_info
        )

        if template and subspace_type in ["lighting", "ventilation"]:
            # client wants a single template
            if (
                subspace_type == "ventilation"
                and template not in subspace_type_info["template"].keys()
            ):
                # find closest template
                years = [int(year) for year in subspace_type_info["template"].keys()]
                years.append(int(template))
                years.sort()
                template_index = years.index(int(template))
                if len(years) > 1:
                    if template_index == 0:
                        template = str(years[template_index + 1])
                    else:
                        template = str(years[template_index - 1])
                else:
                    return

            subspace_type_info = subspace_type_info["template"][template]
    else:
        # client wants all sub space types for given space type
        subspace_type_info = {}
        for subspace_type in [
            "lighting",
            "ventilation",
            "electric_equipment",
            "natural_gas_equipment",
        ]:
            subspace_type_info[subspace_type] = get_subspace_type_info(
                subspace_type, space_type, conn, space_info
            )

            if template and subspace_type in ["lighting", "ventilation"]:
                # client wants a single template
                if (
                    subspace_type == "ventilation"
                    and template
                    not in subspace_type_info[subspace_type]["template"].keys()
                ):
                    # find closest template
                    years = [
                        int(year)
                        for year in subspace_type_info[subspace_type]["template"].keys()
                    ]
                    years.append(int(template))
                    years.sort()
                    template_index = years.index(int(template))
                    if len(years) > 1:
                        if template_index == 0:
                            template = years[template_index + 1]
                        else:
                            template = years[template_index - 1]
                    else:
                        return
                subspace_type_info[subspace_type] = subspace_type_info[subspace_type][
                    "template"
                ][template]
        subspace_type_info["schedules"] = get_schedules(space_info, conn)

    return subspace_type_info


def get_subspace_type_info(
    subspace_type: str, space_type, conn, space_info: dict | None = None
):
    # find correct level 2 table
    level_2_dict = {
        "lighting": "level_2_lighting_space_types",
        "electric_equipment": "level_2_electric_equipment",
        "natural_gas_equipment": "level_2_natural_gas_equipment",
        "ventilation": "level_2_ventilation_space_types",
    }
    level_2_table = level_2_dict[subspace_type]

    # find correct field in level 2 table
    level_2_field = f"{subspace_type}_space_type_name"

    # natural gas equipment space types not in level 1 space types
    if not space_info:
        level_2_key = space_type
    else:
        level_2_key = space_info[level_2_field]

    # proto level 2 data
    raw_subspace_type_info = fetch_records_from_table_by_key_values(
        conn, level_2_table, key_value_dict={level_2_field: level_2_key}
    )

    if subspace_type in ["electric_equipment", "natural_gas_equipment"]:
        # basically return as-is
        if raw_subspace_type_info:
            subspace_type_info = raw_subspace_type_info[0]
        else:
            subspace_type_info = {}
    elif subspace_type in ["lighting", "ventilation"]:
        # return the level 3 data
        level_3_table_field = (
            "level_3_lighting_code_definition_table"
            if subspace_type == "lighting"
            else "level_3_ventilation_definition_table"
        )
        level_3_id_field = (
            "level_3_lighting_code_definition_id"
            if subspace_type == "lighting"
            else "level_3_ventilation_definition_id"
        )

        level_3_table_to_id = {}
        for entry in raw_subspace_type_info:
            level_3_table_to_id[entry[level_3_table_field]] = entry[level_3_id_field]

        subspace_type_info = {"template": {}}
        for table in level_3_table_to_id:
            # table[-4:] is the year
            subspace_type_info["template"][
                table[-4:]
            ] = fetch_a_record_from_table_by_id(conn, table, level_3_table_to_id[table])

    if subspace_type == "lighting":
        subspace_type_info[
            "lighting_space_type_target_illuminance_setpoint"
        ] = raw_subspace_type_info[0]["lighting_space_type_target_illuminance_setpoint"]
        subspace_type_info[
            "lighting_space_type_target_illuminance_setpoint_unit"
        ] = raw_subspace_type_info[0][
            "lighting_space_type_target_illuminance_setpoint_unit"
        ]

    return subspace_type_info


def get_schedules(space_info: dict, conn):
    schedule_name = space_info["schedule_set_name"]
    return fetch_records_from_table_by_key_values(
        conn, "support_schedules", key_value_dict={"name": schedule_name}
    )


def get_lighting(
    max: int | None = None,
    template: str | None = None,
    database_path: str | None = None,
):
    return helpers._get_lighting_or_ventilation_helper(
        "level_3_lighting_90_1_", max, template, database_path
    )


def get_ventilation(
    max: int | None = None,
    template: str | None = None,
    database_path: str | None = None,
):
    return helpers._get_lighting_or_ventilation_helper(
        "level_3_ventilation_62_1_", max, template, database_path
    )


def get_electric_equipment(max: int | None = None, database_path: str | None = None):
    return helpers._get_electric_or_ng_equipment_helper(
        "level_2_electric_equipment", max, database_path
    )


def get_ng_equipment(max: int | None = None, database_path: str | None = None):
    return helpers._get_electric_or_ng_equipment_helper(
        "level_2_natural_gas_equipment", max, database_path
    )


def get_assembly_value(**kwargs):
    # filter out null kwargs
    res = {k: v for k, v in kwargs.items() if v is not None}
    conn = create_connect(res["database_path"])

    del res["database_path"]

    for k in res:
        if k == "template":
            res[k] = f"90.1-{res[k]}"
        elif k == "climate_zone_set":
            res[k] = f"ClimateZone {res[k]}"
        elif k == "intended_surface_type":
            res[k] = res[k].replace('_', " ").title().replace(" ", "")
            print(res[k])
        elif k in ["standards_construction_type", "construction"]:
            res[k] = res[k].replace("_", " ").title()    
        elif k == "building_category":
            res[k] = res[k].title()
        

    if res:
        assembly_values = fetch_records_from_table_by_key_values(
            conn, "envelope_requirement", key_value_dict=res
        )
    else:
        # no filters
        assembly_values = fetch_table(conn, "envelope_requirement")
    return assembly_values


def get_water_heater_data(**kwargs):
    # filter out null kwargs
    res = {k: v for k, v in kwargs.items() if v is not None}

    numerical_filters = ["capacity", "storage", "capacity_per_storage"]

    table_name_prefix = "hvac_minimum_requirement_water_heaters_"

    str_transformation_dict = {"product_class": "caps with space", "fuel_type": "caps without space"}

    table_suffixes = ["90_1", "90_1_prm", "IECC"]

    return helpers.get_min_reqs_data(res, numerical_filters, table_name_prefix, str_transformation_dict, table_suffixes)

def get_boiler_data(**kwargs):
    # filter out null kwargs
    res = {k: v for k, v in kwargs.items() if v is not None}

    numerical_filters = ["capacity"]

    table_name_prefix = "hvac_minimum_requirement_boilers_"

    str_transformation_dict = {"fluid_type": "caps with space", "fuel_type": "caps without space", "draft_type": "caps without space"}

    table_suffixes = ["90_1", "IECC"]

    return helpers.get_min_reqs_data(res, numerical_filters, table_name_prefix, str_transformation_dict, table_suffixes)

def get_chiller_data(**kwargs):
    # filter out null kwargs
    res = {k: v for k, v in kwargs.items() if v is not None}

    numerical_filters = ["capacity"]

    table_name_prefix = "hvac_minimum_requirement_chillers_"

    str_transformation_dict = {"cooling_type": "caps without space", "condenser_type": "caps without space", "compressor_type": "caps with space", "absorption_type": "caps with space"}

    table_suffixes = ["90_1"]

    return helpers.get_min_reqs_data(res, numerical_filters, table_name_prefix, str_transformation_dict, table_suffixes)