"""PQ"""

from typing import Any, Iterable
from typing_extensions import Self
import sympy as sp
import attr
import copy

from my_labs.Georg_Brandl_physics import Q
from my_labs.vne import VNE
from my_labs.calculate import GetSymbol


__all__ = ['PQ', 'Unit']


class Unit(str):
    pass


def convert(value: Any, old_unit: Unit, new_unit: Unit) -> Any|list[Any]:
    if isinstance(value, Iterable):
        return [convert(v, old_unit, new_unit) for v in value]
    q = Q(value, old_unit)
    q.convert(new_unit)
    return q.value


@attr.define()
class PhysicalQuantity(VNE):
    """VNE with unit."""

    unit: Unit = attr.field(default=None)

    def __init__(self, *args, unit: Unit = None, **kwargs) -> None:
        VNE.__init__(self, *args, **kwargs)
        self.unit = unit

    def convert(self, new_unit: Unit) -> None:
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

    symbol: sp.Symbol = attr.field(default='', converter=GetSymbol)

    def __init__(self, *args, symbol: sp.Symbol = "", **kwargs) -> None:
        PhysicalQuantity.__init__(self, *args, **kwargs)
        self.symbol = GetSymbol(symbol)


PQ = PhysicalQuantityWithSymbol
