"""PQ"""

from typing import Any
import sympy as sp
import attr

from .VNE import VNE
from .ipython_physics import Q

from .calculate import _get_symbol

class Unit(str):
    pass


def convert(value: Any, old_unit: Unit, new_unit: Unit) -> Any:
    q = Q(value, old_unit)
    q.convert(new_unit)
    return q.value


@attr.define()
class PhysicalQuantity(VNE):
    """Physical quantity with units."""

    unit: Unit = attr.field(default=None)

    def convert(self, new_unit: Unit):
        self.value = convert(self.value, self.unit, new_unit)
        self.err = convert(self.err, self.unit, new_unit)
        self.unit = new_unit


@attr.define()
class PQwithSymbol(PhysicalQuantity):
    symbol: sp.Symbol = attr.field(default='', converter=_get_symbol)


PQ = PQwithSymbol
