from enum import IntEnum

class AlphaMode(IntEnum):
    """Enum for alpha modes used in texture compression."""
    NONE = 0
    TRANSPARENCY = 1
    PREMULTIPLIED = 2
    