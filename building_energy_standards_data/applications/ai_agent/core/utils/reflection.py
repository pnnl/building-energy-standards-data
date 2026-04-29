from dataclasses import fields

def get_field_weights(descriptor_cls):
    weights = {}
    for f in fields(descriptor_cls):
        weights[f.name] = f.metadata.get("weight", 1.0)
    return weights

def _resolve_enum(enum_cls, value):
    """Try to coerce *value* into an enum member; return None on failure."""
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except (ValueError, KeyError):
        pass
    # Try name-based lookup (case-insensitive)
    for member in enum_cls:
        if member.name.lower() == str(value).lower():
            return member
    return None
