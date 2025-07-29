from enum import IntEnum


class ToneMapper(IntEnum):
    """Enum for Tone mapper modes."""
    LINEAR = 0
    REINHARD = 1
    REINHART = REINHARD
    HALO = 2
    LIGHTMAP = 3