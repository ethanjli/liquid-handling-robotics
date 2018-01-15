"""Various functions to simplify math calculations."""
from typing import Union

def map_value(
    x: Union[int, float], in_min: Union[int, float], in_max: Union[int, float],
    out_min: Union[int, float], out_max: Union[int, float]
) -> float:
    """Maps a value from an input range to a target range.

    Equivalent to Arduino's `map` function.

    Args:
        x: the value to map.
        in_min: the lower bound of the value's current range.
        in_max: the upper bound of the value's current range.
        out_min: the lower bound of the value's target range.
        out_max: the upper bound of the value's target range.

    Returns:
        The mapped value in the target range.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

