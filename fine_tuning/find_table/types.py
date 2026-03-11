from dataclasses import dataclass, field
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
    def from_tokens(cls, tokens: list[str]) -> "Domain":
        table_name = "_".join(tokens)
        prefix_mapping = {
            "envelope": cls.ENVELOPE,
            "hvac": cls.HVAC,
            "exterior": cls.LIGHTING,
            "level_3_lighting": cls.LIGHTING,
            "level_2": cls.SPACE_CLASSIFICATION,
            "level_1": cls.SPACE_CLASSIFICATION,
            "support": cls.SUPPORT,
            "system_requirements": cls.HVAC,
        }
        return next(
            (domain for prefix, domain in prefix_mapping.items() if table_name.startswith(prefix)),
            cls.UNKNOWN
        )

class Topic(StrEnum):
    MINIMUM_REQUIREMENTS = "minimum_requirements"
    LIGHTING_DATA = "lighting_data"
    VENTILATION_DATA = "ventilation_data"
    SPACE_TYPES = "space_types"
    MATERIALS = "materials"
    CONSTRUCTIONS = "constructions"


class System(StrEnum):
    BOILER = "boiler"
    CHILLER = "chiller"
    FURNACE = "furnace"
    HEAT_PUMP = "heat_pump"
    VARIABLE_REFRIGERANT_FLOW_SYSTEM = "variable_refrigerant_flow_system"
    UNITARY_AC = "unitary_ac"
    COMPUTER_ROOM_AC = "computer_room_ac"
    WALKIN_FREEZERS_COOLER = "walkin_freezers_cooler"
    COMMERCIAL_REFRIGERATORS_FREEZERS = "commercial_refrigerators_freezers"
    WATER_HEATERS = "water_heaters"
    FAN_POWER = "fan_power"
    HEAT_REJECTION = "heat_rejection"
    AIR_ECONOMIZER = "air_economizer"
    ENERGY_RECOVERY = "energy_recovery"
    MOTOR = "motor"
    FAN = "fan"
    PUMP = "pump"
    LIGHTING = "lighting"
    ENVELOPE = "envelope"
    THERMAL_BRIDGING = "thermal_bridging"

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> Optional["System"]:
        """Match longest token sequence to a system."""
        mapping = {
            "boilers": cls.BOILER,
            "chillers": cls.CHILLER,
            "furnaces": cls.FURNACE,
            "heat_pumps": cls.HEAT_PUMP,
            "variable_refrigerant_flow_systems": cls.VARIABLE_REFRIGERANT_FLOW_SYSTEM,
            "unitary_air_conditioners": cls.UNITARY_AC,
            "computer_room_air_conditioners": cls.COMPUTER_ROOM_AC,
            "commercial_refrigerators_freezers": cls.COMMERCIAL_REFRIGERATORS_FREEZERS,
            "walkin_freezers_coolers": cls.WALKIN_FREEZERS_COOLER,
            "fan_power": cls.FAN_POWER,
            "water_heaters": cls.WATER_HEATERS,
            "heat_rejection": cls.HEAT_REJECTION,
            "air_economizer": cls.AIR_ECONOMIZER,
            "energy_recovery": cls.ENERGY_RECOVERY,
            "motors": cls.MOTOR,
            "fans": cls.FAN,
            "pumps": cls.PUMP,
            "thermal_bridging": cls.THERMAL_BRIDGING,
            "general_envelope": cls.ENVELOPE

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
    REFRIGERATION = "refrigeration"


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
    domain: Domain = field(metadata={"weight": 1.0, "example": Domain.HVAC})

    topic: Optional[Topic] = field(
        default=None, metadata={"weight": 1.5, "example": Topic.MINIMUM_REQUIREMENTS}
    )

    system: Optional[System] = field(
        default=None, metadata={"weight": 5.0, "example": System.MOTOR}
    )

    sub_system: Optional[SubSystem] = field(
        default=None, metadata={"weight": 3.0, "example": SubSystem.HEATING}
    )

    standard_family: Optional[StandardFamily] = field(
        default=None, metadata={"weight": 1.0, "example": StandardFamily.ASHRAE_90_1}
    )

    standard_year: Optional[int] = field(
        default=None, metadata={"weight": 2.0, "example": 2019}
    )

    compliance_path: CompliancePath = field(
        default=CompliancePath.PRESCRIPTIVE,
        metadata={"weight": 1.0, "example": CompliancePath.PRESCRIPTIVE},
    )
