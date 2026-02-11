from dataclasses import fields
from enum import Enum, StrEnum
from typing import Optional, Type, get_origin, get_args

def get_field_weights(descriptor_cls):
    weights = {}
    for f in fields(descriptor_cls):
        if f.metadata.get("rank", True):
            weights[f.name] = f.metadata.get("weight", 1.0)
    return weights


def build_descriptor_prompt_fields(descriptor_cls):
    lines = []

    for f in fields(descriptor_cls):
        if f.name == "table":
            continue

        field_type = f.type
        origin = get_origin(field_type)

        if origin is Optional:
            field_type = get_args(field_type)[0]

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            values = enum_values(field_type) + [None]
            lines.append(f"- {f.name} (string or null): One of {values}.")
        else:
            lines.append(f"- {f.name} (string or null).")

    return "\n".join(lines)

def enum_values(enum_class: Type[StrEnum]) -> list:
    """Get list of values from a StrEnum."""
    return [e.value for e in enum_class]