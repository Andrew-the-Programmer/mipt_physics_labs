from typing import Any, Iterable
import decimal
import logging
import numpy as np


# type spNumericType = int|float
# type CalculatableType = NumericType|Iterable[NumericType]


def convert_to_numeric_type(value: Any):
    if isinstance(value, Iterable):
        return np.array([convert_to_numeric_type(v) for v in value])
    return float(value)


def fsdp(value: Any) -> int:
    """fsdp - first substantial decimal place"""

    logging.debug(f"fsdp:\n{value=}")

    if isinstance(value, Iterable):
        return max([fsdp(v) for v in value])

    d = decimal.Decimal(float(value)).as_tuple()
    digits, exp = d.digits, d.exponent
    diff: int = len(digits) + exp
    if diff > 0:  # abs(value) > 1
        return 0
    return -diff + 1

def medium(value: Any) -> Any:
    if not isinstance(value, Iterable):
        return value
    return sum(value) / len(value)
