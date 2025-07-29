from enum import IntEnum

class RoundMode(IntEnum):
    """Enum for rounding modes used in texture generation, namely resize operations."""
    NONE = 0
    TO_NEXT_POWER_OF_TWO = 1
    TO_NEAREST_POWER_OF_TWO = 2
    TO_PREVIOUS_POWER_OF_TWO = 3