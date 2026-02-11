from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class Domain(StrEnum):
    ENVELOPE = "envelope"
    HVAC = "hvac"
    LIGHTING = "lighting"
    SPACE_CLASSIFICATION = "space_classification"
    SUPPORT = "support"
    UNKNOWN = "unknown"

    @classmethod
    def from_prefix(cls, prefix: str) -> "Domain":
        return {
            "envelope": cls.ENVELOPE,
            "hvac": cls.HVAC,
            "exterior": cls.LIGHTING,
            "level": cls.SPACE_CLASSIFICATION,
            "support": cls.SUPPORT,
        }.get(prefix, cls.UNKNOWN)


class Topic(StrEnum):
    MINIMUM_REQUIREMENTS = "minimum_requirements"
    REQUIREMENTS = "requirements"
    LIGHTING_DATA = "lighting_data"
    VENTILATION_DATA = "ventilation_data"
    SPACE_TYPES = "space_types"
    MATERIALS = "materials"
    CONSTRUCTIONS = "constructions"
    SCHEDULES = "schedules"
    PERFORMANCE_CURVES = "performance_curves"
    STANDARD_TEMPLATES = "standard_templates"
    OCCUPANT_TYPES = "occupant_types"
    OCCUPANT_BEHAVIOR = "occupant_behavior"
    LIGHTING_TECHNOLOGIES = "lighting_technologies"


class DataRole(StrEnum):
    REQUIREMENTS = "requirements"
    REFERENCE_DATA = "reference_data"
    NORMATIVE_INPUTS = "normative_inputs"
    CLASSIFICATION = "classification"
    UNKNOWN = "unknown"

class ClassificationType(StrEnum):
    TAXONOMY = "taxonomy"
    SUBCLASSIFICATION = "subclassification"

class System(StrEnum):
    BOILER = "boiler"
    CHILLER = "chiller"
    FURNACE = "furnace"
    HEAT_PUMP = "heat_pump"
    VRF = "vrf"
    UNITARY_AC = "unitary_ac"
    CRAC = "crac"
    WATER_HEATER = "water_heater"
    HEAT_REJECTION = "heat_rejection"
    AIR_ECONOMIZER = "air_economizer"
    ENERGY_RECOVERY = "energy_recovery"
    MOTOR = "motor"
    FAN = "fan"
    PUMP = "pump"
    LIGHTING = "lighting"

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> Optional["System"]:
        """Match longest token sequence to a system."""
        mapping = {
            "boilers": cls.BOILER,
            "chillers": cls.CHILLER,
            "furnaces": cls.FURNACE,
            "heat_pumps": cls.HEAT_PUMP,
            "variable_refrigerant_flow_systems": cls.VRF,
            "unitary_air_conditioners": cls.UNITARY_AC,
            "computer_room_air_conditioners": cls.CRAC,
            "water_heaters": cls.WATER_HEATER,
            "heat_rejection": cls.HEAT_REJECTION,
            "air_economizer": cls.AIR_ECONOMIZER,
            "energy_recovery": cls.ENERGY_RECOVERY,
            "motors": cls.MOTOR,
            "fans": cls.FAN,
            "pumps": cls.PUMP,
        }
        for i in range(len(tokens)):
            for j in range(len(tokens), i, -1):
                candidate = "_".join(tokens[i:j])
                if candidate in mapping:
                    return mapping[candidate]
        return None


class SubSystem(StrEnum):
    COOLING = "cooling"
    HEATING = "heating"
    VENTILATION = "ventilation"


class StandardFamily(StrEnum):
    ASHRAE_90_1 = "ASHRAE_90_1"
    ASHRAE_62_1 = "ASHRAE_62_1"
    ASHRAE_189_1 = "ASHRAE_189_1"
    IECC = "IECC"


class CompliancePath(StrEnum):
    PRESCRIPTIVE = "prescriptive"
    APPENDIX_G = "appendix_g"


@dataclass
class TableDescriptor:
    table: str
    domain: Domain
    topic: Optional[Topic] = None
    data_role: DataRole = DataRole.UNKNOWN
    classification_type: Optional[ClassificationType] = None
    system: Optional[System] = None
    sub_system: Optional[SubSystem] = None
    standard_family: Optional[StandardFamily] = None
    standard_year: Optional[int] = None
    compliance_path: CompliancePath = CompliancePath.PRESCRIPTIVE