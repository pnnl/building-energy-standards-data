import csv
import json


def read_csv_to_tuples(csv_dir):
    """
    Read csv, convert each row to a tuple
    :param csv_dir:
    :return: list<tuple> list of tuple
    """
    table_list = []
    with open(csv_dir) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            # remove empty strings in the record
            new_row = [cell if cell else None for cell in row]
            table_list.append(tuple(new_row))

    return table_list


def read_csv_to_list_dict(csv_dir):
    """
    Read csv, convert to list of dictionaries
    :param csv_dir:
    :return: list<dict> list of dictionary
    """
    with open(csv_dir, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        table_list = [
            {key: row[key] for key in row if key != "id"} for row in csv_reader
        ]
    return table_list


def read_json_to_list_dict(json_dir):
    """
    Read json, convert to list of dictionaries
    :param json_dir:
    :return: list<dict> list of dictionary
    """
    with open(json_dir, mode="r") as json_file:
        json_table = json.loads(json_file.read())
        table_list = [{key: record[key] for key in record if key != "id"} for record in json_table]
    return table_list
def read_nested_json_to_list_dict(json_dir):
    """
    Read nested json, convert to list of dictionaries
    :param json_dir: str
    :return: list<dict> list of dictionary
    """
    with open(json_dir, mode="r") as json_file:
        json_table = json.loads(json_file.read())
        table_list = []
        for record in json_table:
            expanded_records = expand_nested_dict(record)
            table_list.extend(expanded_records)
    return table_list

def expand_nested_dict(d):
    """
    Expand a nested dictionary into multiple records
    :param d: dict
    :return: list of dicts
    """
    base_record = {k: v for k, v in d.items() if not isinstance(v, dict)}
    nested_dicts = {k: v for k, v in d.items() if isinstance(v, dict)}

    if not nested_dicts:
        return [base_record]

    expanded_records = [{}]

    for key, nested in nested_dicts.items():
        temp_records = []
        for expanded_record in expanded_records:
            if isinstance(nested, dict):
                for sub_key, sub_value in nested.items():
                    new_record = expanded_record.copy()
                    new_record[f"{key}_{sub_key}"] = sub_value
                    temp_records.append(new_record)
            elif isinstance(nested, list):
                for sub_dict in nested:
                    for sub_key, sub_value in sub_dict.items():
                        new_record = expanded_record.copy()
                        new_record[f"{key}_{sub_key}"] = sub_value
                        temp_records.append(new_record)
        expanded_records = temp_records

    final_records = []
    for expanded_record in expanded_records:
        final_record = base_record.copy()
        final_record.update(expanded_record)
        final_records.append(final_record)

    return final_records

def is_float(element: any) -> bool:
    """
    Test to verify if an element is float data type
    :param element:
    :return:
    """
    if element is None:
        return False
    try:
        float(element)
    except ValueError:
        return False
    return True


def getattr_either(key: str, record: dict, option=None):
    """
    A helper function to retrieve a key from a record object (dict) with an option for reject solution.
    :param key: key
    :param record: dictionary that could contain value for the key.
    :param option: value return when reject (optional), default is None
    :return: value
    """
    if record.get(key) == "":  # used for reading data from CSV
        return option
    elif record.get(key) is None:  # used for readting data from CSV
        return option
    else:
        return f"{record[key]}"
