"""Enums for reagents used in imaging experiments"""

from enum import Enum


class StainType(str, Enum):
    """Stain types for probes describing what is being labeled"""

    RNA = "RNA"
    NUCLEAR = "Nuclear"
    FILL = "Fill"


class FluorophoreType(str, Enum):
    """Fluorophores types"""

    ALEXA = "Alexa Fluor"
    ATTO = "Atto"
    CF = "CF"
    CYANINE = "Cyanine"
    DYLIGHT = "DyLight"
