from typing import List, Optional, Tuple

from fine_tuning.find_table.types import (
    TableDescriptor,
    Domain,
    Topic,
    DataRole,
    ClassificationType,
    System,
    SubSystem,
    StandardFamily,
    CompliancePath,
)


def parse_compliance_path(tokens: List[str]) -> CompliancePath:
    return (
        CompliancePath.APPENDIX_G
        if tokens[-1] == "prm"
        else CompliancePath.PRESCRIPTIVE
    )


def parse_topic(tokens: List[str]) -> Optional[Topic]:
    if "minimum" in tokens and "requirements" in tokens:
        return Topic.MINIMUM_REQUIREMENTS
    if "requirements" in tokens:
        return Topic.REQUIREMENTS
    if "lighting" in tokens:
        return Topic.LIGHTING_DATA
    if "ventilation" in tokens:
        return Topic.VENTILATION_DATA
    if "space" in tokens and "types" in tokens:
        return Topic.SPACE_TYPES
    return None


def parse_sub_system(tokens: List[str]) -> Optional[SubSystem]:
    if "cooling" in tokens:
        return SubSystem.COOLING
    if "heating" in tokens:
        return SubSystem.HEATING
    if "ventilation" in tokens:
        return SubSystem.VENTILATION
    return None


def parse_standard_family(tokens: List[str]) -> Optional[StandardFamily]:
    # Check for IECC (case-insensitive)
    if any(t.upper() == "IECC" for t in tokens):
        return StandardFamily.IECC

    # Check for ASHRAE standards by number pattern
    if "90" in tokens and "1" in tokens:
        return StandardFamily.ASHRAE_90_1
    if "62" in tokens and "1" in tokens:
        return StandardFamily.ASHRAE_62_1
    if "189" in tokens and "1" in tokens:
        return StandardFamily.ASHRAE_189_1

    return None


def parse_standard(tokens: List[str]) -> Tuple[Optional[StandardFamily], Optional[int]]:
    standard_family = parse_standard_family(tokens)
    standard_year = parse_standard_year(tokens)
    return standard_family, standard_year


def parse_standard_year(tokens: List[str]) -> Optional[int]:
    for t in tokens:
        if t.isdigit() and len(t) == 4:
            return int(t)
    return None


def parse_classification_type(
    tokens: List[str],
) -> Optional[ClassificationType]:
    domain = parse_domain(tokens)
    topic = parse_topic(tokens)

    if domain != Domain.SPACE_CLASSIFICATION:
        return None

    if topic == Topic.SPACE_TYPES:
        return ClassificationType.TAXONOMY

    if "subtypes" in tokens or "subspace" in tokens:
        return ClassificationType.SUBCLASSIFICATION

    return None


def parse_data_role(tokens: List[str]) -> DataRole:
    domain = parse_domain(tokens)

    role_map = {
        Domain.SUPPORT: DataRole.REFERENCE_DATA,
        Domain.SPACE_CLASSIFICATION: DataRole.CLASSIFICATION,
        Domain.UNKNOWN: DataRole.UNKNOWN,
    }
    return role_map.get(domain, DataRole.REQUIREMENTS)


def parse_domain(tokens: List[str]) -> Domain:
    return Domain.from_prefix(tokens[0])


def parse_system(tokens: List[str]) -> System:
    return System.from_tokens(tokens)


class ParsingRule:
    def __init__(self, field_name, fn):
        self.field_name = field_name
        self.fn = fn

    def apply(self, tokens):
        return self.field_name, self.fn(tokens)


compliance_path_rule = ParsingRule("compliance_path", parse_compliance_path)
domain_rule = ParsingRule("domain", parse_domain)
topic_rule = ParsingRule("topic", parse_topic)
system_rule = ParsingRule("system", parse_system)
sub_system_rule = ParsingRule("sub_system", parse_sub_system)
standard_family_rule = ParsingRule("standard_family", parse_standard_family)
standard_year_rule = ParsingRule("standard_year", parse_standard_year)

RULES: List[ParsingRule] = [
    compliance_path_rule,
    domain_rule,
    topic_rule,
    system_rule,
    sub_system_rule,
    standard_family_rule,
    standard_year_rule,
]
