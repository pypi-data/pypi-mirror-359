from enum import IntEnum

class WrapMode(IntEnum):
    """Enum for texture wrap modes."""
    CLAMP = 0
    REPEAT = 1
    MIRROR = 2