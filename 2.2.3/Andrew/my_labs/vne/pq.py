"""PQ"""

from typing import Any, Iterable
import copy
import attr
from typing_extensions import Self
import sympy as sp

from my_labs.Georg_Brandl_physics import Q
from my_labs.vne import VNE
from my_labs.my_sp import GetSymbol


__all__ = ["PQ", "Unit"]


def _get_q(unit: Any) -> Q:
    return Q(value=1, unit=unit)


class Unit:
    value: str = None

    def __init__(self, value: Any):
        if value is None:
            self.value = None
        elif isinstance(value, Unit):
            self.value = value.value
        else:
            self.value = str(value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)

    def __truediv__(self, other: Self) -> Self:
        try:
            n = self._get_q()
        except ValueError:
            n = 1

        try:
            d = other._get_q()
        except ValueError:
            d = 1

        v: Q = n / d

        try:
            return Unit(v.unit)
        except AttributeError:
            return Unit(None)

    def __bool__(self) -> bool:
        return bool(self.value)

    def _get_q(self) -> Q:
        if self.value is None:
            raise ValueError("Could not _get_q of Unit: Value is None")
        return _get_q(self.value)


def convert(value: Any, old_unit: Unit, new_unit: Unit) -> Any | list[Any]:
    if isinstance(value, Iterable):
        return [convert(v, old_unit, new_unit) for v in value]
    q = Q(value, old_unit.value)
    q.convert(new_unit.value)
    return q.value


@attr.define()
class PhysicalQuantity(VNE):
    """VNE with unit."""

    unit: Unit = attr.field()

    def __init__(self, *args, unit: Unit = None, **kwargs) -> None:
        VNE.__init__(self, *args, **kwargs)
        self.unit = Unit(unit)

    def convert(self, new_unit: Unit) -> None:
        new_unit = Unit(new_unit)
        self.value = convert(self.value, self.unit, new_unit)
        self.err = convert(self.err, self.unit, new_unit)
        self.unit = new_unit

    def converted(self, new_unit: Unit) -> Self:
        c = copy.copy(self)
        c.convert(new_unit)
        return c


@attr.define()
class PhysicalQuantityWithSymbol(PhysicalQuantity):
    """PhysicalQuantity with unit."""

    symbol: sp.Symbol = attr.field()

    def __init__(self, *args, symbol: sp.Symbol = None, **kwargs) -> None:
        PhysicalQuantity.__init__(self, *args, **kwargs)
        self.set_symbol(symbol)

    def get_label(self):
        s = self.symbol
        u = self.unit
        if not s:
            raise ValueError("Could not get label: no symbol")
        if not u:
            return s
        return f"{s}, {u}"

    def set_symbol(self, new_symbol):
        if isinstance(new_symbol, str):
            self.symbol = GetSymbol(new_symbol)
        else:
            self.symbol = new_symbol


PQ = PhysicalQuantityWithSymbol
