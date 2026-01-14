from enum import StrEnum

class Domain(StrEnum):
    ENVELOPE = "envelope"
    HVAC = "hvac"
    EXTERIOR_LIGHTING = "exterior_lighting"
    SYSTEM = "system"
    SPACE_CLASSIFICATION = "space_classification"
    SUPPORT = "support"
    UNKNOWN = "unknown"

class Topic(StrEnum):
    MINIMUM_REQUIREMENTS = "minimum_requirements"
    REQUIREMENTS = "requirements"
    LIGHTING_DATA = "lighting_data"
    VENTILATION_DATA = "ventilation_data"
    SPACE_TYPES = "space_types"
    LIGHTING_TECHNOLOGIES = "lighting_technologies"
    OCCUPANT_PHYSICAL_CHARACTERISTICS = "occupant_physical_characteristics"
    OCCUPANT_ENERGY_BEHAVIOR = "occupant_energy_behavior"
    STANDARD_TEMPLATES = "standard_templates"
    PERFORMANCE_CURVES = "performance_curves"
    SCHEDULES = "schedules"

class DataRole(StrEnum):
    REFERENCE_DATA = "reference_data"
    REQUIREMENTS = "requirements"
    NORMATIVE_INPUTS = "normative_inputs"
    CLASSIFICATION = "classification"
    UNKNOWN = "unknown"

class ClassificationType(StrEnum):
    TAXONOMY = "taxonomy"
    SUBCLASSIFICATION = "subclassification"

class System(StrEnum):
    VRF = "vrf"
    UNITARY_AC = "unitary_ac"
    CRAC = "crac"
    WATER_HEATER = "water_heater"
    HEAT_REJECTION = "heat_rejection"
    AIR_ECONOMIZER = "air_economizer"
    ENERGY_RECOVERY = "energy_recovery"
    BOILER = "boiler"
    CHILLER = "chiller"
    FURNACE = "furnace"
    MOTOR = "motor"
    LIGHTING = "lighting"

class SubSystem(StrEnum):
    COOLING = "cooling"
    HEATING = "heating"

class StandardFamily(StrEnum):
    IECC = "IECC"
    ASHRAE_90_1 = "ASHRAE_90_1"
    ASHRAE_62_1 = "ASHRAE_62_1"
    ASHRAE_189_1 = "ASHRAE_189_1"

class CompliancePath(StrEnum):
    APPENDIX_G = "appendix_g"
    PRESCRIPTIVE = "prescriptive"
