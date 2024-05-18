""" :3 """

import sympy as sp
import attr

from my_labs.my_sp import GetSymbol


@attr.define()
class Symbolic:
    """Class with symbol."""

    symbol: sp.Symbol = attr.field(default='', converter=GetSymbol)
