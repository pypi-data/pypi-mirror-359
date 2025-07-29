from enum import IntEnum

class PixelType(IntEnum):
    """Enum for pixel types."""
    UnsignedNorm = 0
    SignedNorm = 1
    UnsignedInt = 2
    SignedInt = 3
    Float = 4
    UnsignedFloat = 5
    SharedExp = 6