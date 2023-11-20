from database_engine.database import create_connect
from query.fetch.database_table import (
    fetch_table,
    fetch_table_names_containing_keyword,
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


def _get_value_and_remove_from_dict(res: dict, key: str):
    val = res.pop(key, None)
    return val


def _water_heater_reqs_filter(
    reqs: list,
    capacity: float | None = None,
    storage: float | None = None,
    capacity_per_storage: float | None = None,
):
    if capacity:
        reqs = [
            item
            for item in reqs
            if item["minimum_capacity"] is None
            or (item["minimum_capacity"] <= capacity <= item["maximum_capacity"])
        ]
    if storage:
        reqs = [
            item
            for item in reqs
            if item["minimum_storage"] is None
            or item["minimum_storage"] <= storage <= item["maximum_storage"]
        ]
    if capacity_per_storage:
        reqs = [
            item
            for item in reqs
            if item["minimum_capacity_per_storage"] is None
            or item["minimum_capacity_per_storage"]
            <= capacity_per_storage
            <= item["maximum_capacity_per_storage"]
        ]
    return reqs
