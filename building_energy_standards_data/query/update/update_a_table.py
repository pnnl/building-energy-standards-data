import sqlite3


def update_a_table(
    conn: sqlite3.Connection, table_name: str, update_dict: dict, search_condition: str
) -> bool:
    """
    Update a table data based on search conditions and update values -
    there is no order by and limit.

    Args:
        conn: sqlite3.Connection
        table_name: table name
        update_dict: dictionary contains the key-value data pair where key is the table column header and value is
        the new value. Note, None is allowed and will not add to the updates
        search_condition: str a search criteria string composed by the client end. e.g. "id = 11"

    Returns:
        True if update successfully, False otherwise
    """

    set_str_value = [
        f"{key}='{update_dict[key]}'" for key in update_dict.keys() if update_dict[key]
    ]

    UPDATE_QUERY = f"""
        UPDATE {table_name}
        SET {','.join(set_str_value)}
        WHERE {search_condition}
    """

    try:
        conn.execute(UPDATE_QUERY)
        conn.commit()
        return True
    except sqlite3.Error:
        return False
