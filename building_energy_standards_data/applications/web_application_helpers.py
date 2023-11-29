from database_engine.database import create_connect
from query.fetch.database_table import (
    fetch_table,
    fetch_table_names_containing_keyword,
    fetch_records_from_table_by_key_values
)


def _get_lighting_or_ventilation_helper(
    level_3_base: str,
    max: int | None = None,
    template: str | None = None,
    database_path: str | None = None,
):
    conn = create_connect(database_path)
    if template:
        table_name = f"{level_3_base}{template}"
        table = fetch_table(conn, table_name)
        if max and len(table) > max:
            table = table[0:max]
    else:
        table = {"template": {}}
        table_names = fetch_table_names_containing_keyword(conn, level_3_base)
        for table_name in table_names:
            year = table_name.split(level_3_base)[1]
            table["template"][year] = fetch_table(conn, table_name)
            if max and len(table["template"][year]) > max:
                table["template"][year] = table["template"][year][0:max]
    return table


def _get_electric_or_ng_equipment_helper(
    level_2_table: str, max: int | None = None, database_path: str | None = None
):
    conn = create_connect(database_path)
    table = fetch_table(conn, level_2_table)
    if max and len(table) > max:
        table = table[0:max]
    return table

def _transform_str_for_database(res: dict, transformation_dict: dict):
    for k, v in transformation_dict.items():
        if res.get(k) is not None:
            res[k] = res[k].replace("_", " ")
            res[k] = res[k].title()
            if v == "caps without space":
                res[k] = res[k].replace(" ", "")
    return res

def _transform_template_name_for_database(res: dict, prefix: str):
    table_name = None
    if "template" in res.keys():
        if "IECC" in res["template"].value:
            table_name_suffix = "IECC"
        elif "PRM" in res["template"].value:
            table_name_suffix = "90_1_prm"
        else:
            table_name_suffix = "90_1"
        table_name = f"{prefix}{table_name_suffix}"
    return table_name

def _min_reqs_filter(
    reqs: list,
    numerical_filter_dict: dict
):
    for k, v in numerical_filter_dict.items():
        if v:
            reqs = [
                item
                for item in reqs
                if item[f"minimum_{k}"] is None
                or (item[f"minimum_{k}"] <= v <= item[f"maximum_{k}"])
            ]
    return reqs

def get_min_reqs_data(res, numerical_filters, table_name_prefix, str_transformation_dict, table_suffixes):
    # filter out null kwargs

    numerical_filter_dict = {k: res.pop(k, None) for k in numerical_filters}

    conn = create_connect(res.pop("database_path"))

    table_name = _transform_template_name_for_database(res, table_name_prefix)

    res = _transform_str_for_database(res, str_transformation_dict)

    if table_name:
        reqs = fetch_records_from_table_by_key_values(
            conn, table_name, key_value_dict=res
        )
        reqs = _min_reqs_filter(
            reqs, numerical_filter_dict
        )
        return reqs
    else:
        table_dict = {
            f"{table_name_prefix}{suffix}": None
            for suffix in table_suffixes
        }
        for table_name in table_dict:
            if res:
                # filter table
                reqs = fetch_records_from_table_by_key_values(
                    conn, table_name, key_value_dict=res
                )
            else:
                # get entire table
                reqs = fetch_table(conn, table_name)
            reqs = _min_reqs_filter(reqs, numerical_filter_dict)
            if len(table_dict.keys()) > 1:
                table_dict[table_name] = reqs
            else:
                table_dict = reqs
    return table_dict
