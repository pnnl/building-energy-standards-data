from dataclasses import fields
from enum import Enum, StrEnum
from typing import Optional, Type, Union, get_origin, get_args, TYPE_CHECKING
import json

from fine_tuning.find_table.rules import RULES
from fine_tuning.find_table.types import TableDescriptor


def get_field_weights(descriptor_cls):
    weights = {}
    for f in fields(descriptor_cls):
        weights[f.name] = f.metadata.get("weight", 1.0)
    return weights


def get_descriptor_example(descriptor_cls):
    example = {}
    for f in fields(descriptor_cls):
        example[f.name] = f.metadata.get("example", None)
    return example


def unwrap_optional(field_type):
    origin = get_origin(field_type)

    if origin is Union:
        args = get_args(field_type)
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0], True

    return field_type, False


def build_descriptor_prompt(descriptor_cls):
    lines = []

    for f in fields(descriptor_cls):
        field_type, is_optional = unwrap_optional(f.type)

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            values = [e.value for e in field_type]
            if is_optional:
                values.append(None)

            lines.append(
                f"- {f.name} (string{' or null' if is_optional else ''}): "
                f"One of {values}."
            )
        else:
            lines.append(f"- {f.name} (string{' or null' if is_optional else ''}).")

    return "\n".join(lines)


def enum_values(enum_class: Type[StrEnum]) -> list:
    """Get list of values from a StrEnum."""
    return [e.value for e in enum_class]


def dict_to_prompt_string(
    data: dict,
    indent: int = 0,
    skip_none: bool = True,
) -> str:
    """
    Convert a dictionary into a nicely formatted, prompt-friendly string.
    """

    lines = []
    indent_str = "  " * indent

    items = data.items()

    for key, value in items:
        if skip_none and value is None:
            continue

        if isinstance(value, dict):
            lines.append(f"{indent_str}{key}:")
            lines.append(
                dict_to_prompt_string(
                    value,
                    indent=indent + 1,
                    skip_none=skip_none,
                )
            )

        elif isinstance(value, (list, tuple)):
            lines.append(f"{indent_str}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(
                        dict_to_prompt_string(
                            item,
                            indent=indent + 1,
                            skip_none=skip_none,
                        )
                    )
                else:
                    lines.append(f"{'  ' * (indent + 1)}- {item}")

        else:
            lines.append(f"{indent_str}{key}: {value}")

    return "\n".join(lines)
