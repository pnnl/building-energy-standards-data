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


class TableParser:
    """Parses table names into structured TableDescriptor objects."""

    def parse(self, table: str) -> TableDescriptor:
        tokens = table.split("_")

        compliance_path = self._parse_compliance_path(tokens)
        domain = Domain.from_prefix(tokens[0])
        topic = self._parse_topic(tokens)
        system = System.from_tokens(tokens)
        sub_system = self._parse_sub_system(tokens)
        standard_family, standard_year = self._parse_standard(tokens)
        data_role = self._parse_data_role(domain)

        # Schema-driven refinements
        topic, system, data_role = self._refine_support_domain(
            table, domain, topic, system, data_role
        )
        classification_type = self._parse_classification_type(domain, topic, tokens)

        return TableDescriptor(
            table=table,
            domain=domain,
            topic=topic,
            data_role=data_role,
            classification_type=classification_type,
            system=system,
            sub_system=sub_system,
            standard_family=standard_family,
            standard_year=standard_year,
            compliance_path=compliance_path,
        )

    def _parse_compliance_path(self, tokens: List[str]) -> CompliancePath:
        return (
            CompliancePath.APPENDIX_G
            if tokens[-1] == "prm"
            else CompliancePath.PRESCRIPTIVE
        )

    def _parse_topic(self, tokens: List[str]) -> Optional[Topic]:
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

    def _parse_sub_system(self, tokens: List[str]) -> Optional[SubSystem]:
        if "cooling" in tokens:
            return SubSystem.COOLING
        if "heating" in tokens:
            return SubSystem.HEATING
        if "ventilation" in tokens:
            return SubSystem.VENTILATION
        return None

    def _parse_standard(
        self, tokens: List[str]
    ) -> Tuple[Optional[StandardFamily], Optional[int]]:
        standard_family = self._parse_standard_family(tokens)
        standard_year = self._parse_standard_year(tokens)
        return standard_family, standard_year

    def _parse_standard_family(self, tokens: List[str]) -> Optional[StandardFamily]:
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

    def _parse_standard_year(self, tokens: List[str]) -> Optional[int]:
        for t in tokens:
            if t.isdigit() and len(t) == 4:
                return int(t)
        return None

    def _parse_data_role(self, domain: Domain) -> DataRole:
        role_map = {
            Domain.SUPPORT: DataRole.REFERENCE_DATA,
            Domain.SPACE_CLASSIFICATION: DataRole.CLASSIFICATION,
            Domain.UNKNOWN: DataRole.UNKNOWN,
        }
        return role_map.get(domain, DataRole.REQUIREMENTS)

    def _refine_support_domain(
        self,
        table: str,
        domain: Domain,
        topic: Optional[Topic],
        system: Optional[System],
        data_role: DataRole,
    ) -> Tuple[Optional[Topic], Optional[System], DataRole]:
        if domain != Domain.SUPPORT:
            return topic, system, data_role

        # Direct table name mappings
        refinements = {
            "support_lighting_technologies": (
                Topic.LIGHTING_TECHNOLOGIES,
                System.LIGHTING,
                data_role,
            ),
            "support_occupant_physical_characteristics": (
                Topic.OCCUPANT_TYPES,
                system,
                data_role,
            ),
            "support_occupant_energy_behavior": (
                Topic.OCCUPANT_BEHAVIOR,
                system,
                DataRole.NORMATIVE_INPUTS,
            ),
            "support_standard_templates": (
                Topic.STANDARD_TEMPLATES,
                system,
                data_role,
            ),
            "support_performance_curves": (
                Topic.PERFORMANCE_CURVES,
                system,
                data_role,
            ),
        }

        if table in refinements:
            return refinements[table]

        # Pattern-based refinements
        if "schedule" in table:
            return Topic.SCHEDULES, system, DataRole.NORMATIVE_INPUTS
        if "material" in table:
            return Topic.MATERIALS, system, data_role
        if "construction" in table:
            return Topic.CONSTRUCTIONS, system, data_role

        return topic, system, data_role

    def _parse_classification_type(
        self,
        domain: Domain,
        topic: Optional[Topic],
        tokens: List[str],
    ) -> Optional[ClassificationType]:
        if domain != Domain.SPACE_CLASSIFICATION:
            return None

        if topic == Topic.SPACE_TYPES:
            return ClassificationType.TAXONOMY

        if "subtypes" in tokens or "subspace" in tokens:
            return ClassificationType.SUBCLASSIFICATION

        return None
