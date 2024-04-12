import pandas as pd
import pathlib as pl
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import copy
import attr
import ipython_physics as phs
from typing_extensions import Self
import math
import sympy as sp

from sympy.core.symbol import Symbol
from sympy import init_printing, init_session, pprint


@attr.define(kw_only=True)
class Qe:
    value: phs.Q = attr.field()
    err: phs.Q = attr.field()
    symbol: Symbol = attr.field(default=None)

    def __init__(
        self,
        value_v: float = None,
        err_v: float = None,
        unit: str = None,
        *,
        value: phs.Q = None,
        err: phs.Q = None,
        symbol: Symbol = None,
    ) -> None:
        if value is not None:
            self.value = value
        if err is not None:
            self.err = err
        if value_v is not None:
            self.value = phs.Q(value_v, unit)
        if err_v is not None:
            self.err = phs.Q(err_v, unit)
        if unit is not None:
            self.convert(unit)
        self.symbol = symbol

    def eps(self):
        return self.err / self.value

    def condensed_repr(self, notation: str = ".1E") -> str:
        self.convert(self.value.unit)
        return f"({self.value.value :{notation}} +- {self.err.value :{notation}}) {self.value.unit}"

    def full_repr(self) -> str:
        return f"{self.symbol} = {self.value} +- {self.err}"

    def __str__(self):
        return self.condensed_repr()

    def __repr__(self):
        return self.full_repr()

    def __neg__(self):
        return Qe(value=-self.value, err=self.err)

    def _sum(self, other: Self, sign1, sign2):
        value: phs.Q = self.value._sum(other.value, sign1, sign2)
        err: phs.Q = self.err._sum(other.err, sign1, sign2)
        return self.__class__(value=value, err=err)

    def __add__(self, other):
        return self._sum(other, 1, 1)

    __radd__ = __add__

    def __sub__(self, other):
        return self._sum(other, 1, -1)

    def __rsub__(self, other):
        return self._sum(other, -1, 1)

    def __eq__(self, other):
        diff = self._sum(other, 1, -1)
        return diff.value == 0

    def __lt__(self, other):
        diff = self._sum(other, 1, -1)
        return diff.value < 0

    def __mul__(self, other):
        if isinstance(other, Qe):
            other_eps = other.eps()
            value: phs.Q = self.value * other.value
        else:
            other_eps = 0
            value: phs.Q = self.value * other

        err: phs.Q = value * math.sqrt(self.eps() ** 2 + other_eps**2)

        return self.__class__(value=value, err=err)

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, Qe):
            other_eps = other.eps()
            value: phs.Q = self.value / other.value
        else:
            other_eps = 0
            value: phs.Q = self.value / other

        err: phs.Q = value * math.sqrt(self.eps() ** 2 + other_eps**2)

        return self.__class__(value=value, err=err)

    __truediv__ = __div__

    def __pow__(self, other):
        value: phs.Q = pow(self.value, other)
        err: phs.Q = value * self.eps() * math.sqrt(abs(other))
        return self.__class__(value=value, err=err)

    def convert(self, unit):
        self.value.convert(unit)
        self.err.convert(unit)
