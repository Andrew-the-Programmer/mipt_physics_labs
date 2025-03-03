import math
import uuid
import pandas as pd
import pathlib as pl
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import copy
import attr
from typing_extensions import Self
import sympy as sp
from typing import Iterable

import physics.ipython_physics as phs


def get_value(value) -> float:
    if isinstance(value, phs.Q):
        return value.value
    elif isinstance(value, Qe):
        return get_value(value.value)
    elif isinstance(value, QeStack):
        return get_value(value.values)
    elif isinstance(value, Iterable):
        return [get_value(value) for value in value]
    else:
        return value


def get_err(value) -> float:
    if isinstance(value, Qe):
        return get_value(value.err)
    if isinstance(value, Iterable):
        return [get_err(v) for v in value]
    else:
        return None


def get_unit(value) -> str:
    if isinstance(value, phs.Q):
        return value.unit
    elif isinstance(value, Qe):
        return get_unit(value.value)
    else:
        return None


def generate_symbol(value):
    if isinstance(value, str):
        return sp.Symbol(value)
    if isinstance(value, sp.Symbol):
        return value
    else:
        raise ValueError("Invalid value type")


def get_err_symbol(symbol) -> sp.Symbol:
    return generate_symbol(f"_err_{symbol}")


def _create_unique_symbol() -> sp.Symbol:
    return generate_symbol(f"unique_sp_Symbol{uuid.uuid4()}")


@attr.define(kw_only=True)
class Qe:
    value: phs.Q | float = attr.field()
    err: phs.Q | float = attr.field()
    symbol: sp.Symbol = attr.field(default=None)

    def __init__(
        self,
        value_v: float = None,
        err_v: float = None,
        unit: str = None,
        *,
        value: phs.Q = None,
        err: phs.Q = None,
        symbol: sp.Symbol = None,
    ) -> None:
        if symbol is not None:
            self.symbol = generate_symbol(symbol)
        else:
            self.symbol = _create_unique_symbol()
        if value is not None:
            self.value = value
        elif value_v is not None:
            if unit is None:
                self.value = value_v
            else:
                self.value = phs.Q(value_v, unit)
        else:
            raise ValueError("value not specified")
        if err is not None:
            self.err = err
        elif err_v is not None:
            if unit is None:
                self.err = err_v
            else:
                self.err = phs.Q(err_v, unit)
        else:
            raise ValueError("err not specified")
        if unit is not None:
            self.convert(unit)
        else:
            self.symbol = _create_unique_symbol()

    def eps(self):
        return self.err / self.value

    def condensed_repr(self, notation: str = ".1E") -> str:
        return f"({get_value(self) :{notation}} +- {get_err(self) :{notation}}) {get_unit(self)}"

    def full_repr(self) -> str:
        return f"{self.symbol} = {self.value} +- {self.err}"

    def __str__(self):
        return self.condensed_repr("")

    def __repr__(self):
        return str(self)

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

    # TODO:
    def normalize(self):
        pass

    def get_value(self) -> float:
        if isinstance(self.value, phs.Q):
            return self.value.value
        else:
            return self.value

    def get_err(self) -> float:
        if isinstance(self.err, phs.Q):
            return self.err.value
        else:
            return self.err


def calculate_value(equation, subs: dict[sp.Symbol | str, Qe | float]):
    normal_subs = dict()
    stack_subs = dict()
    for symbol, value in subs.items():
        if isinstance(value, Iterable):
            stack_subs[symbol] = value
        else:
            normal_subs[symbol] = get_value(value)
    equation = equation.evalf(subs=normal_subs)
    if not stack_subs:
        return equation
    subs: list[dict] = []
    for symbol, values in stack_subs.items():
        for i, value in enumerate(values):
            if i < len(subs):
                subs[i][symbol] = value
            else:
                subs.append({symbol: value})
    return [calculate_value(equation, subs=sub) for sub in subs]


def calculate_err(equation, subs: dict[sp.Symbol | str, Qe | float]):
    err_eq = sp.sqrt(
        sum(
            [
                sp.diff(equation, symbol) ** 2 * get_err_symbol(symbol) ** 2
                # sp.diff(equation, symbol) ** 2 * sp.sp.Symbol(f'd_{symbol}') ** 2
                for symbol in subs.keys()
            ]
        )
    )
    for symbol in subs.keys():
        subs[get_err_symbol(symbol)] = get_err(subs[symbol])
    err_eq = err_eq.factor()
    res = calculate_value(err_eq, {})
    return calculate_value(err_eq, subs)


def calculate(equation, subs: dict[sp.Symbol | str, Qe | float]) -> Qe:
    value = calculate_value(equation, subs)
    print(value)
    err = calculate_err(equation, subs)
    return Qe(value=value, err=err)


@attr.define(kw_only=True)
class QeStack:
    values: np.ndarray[Qe] = attr.field()
    symbol: sp.Symbol = attr.field(default=None)

    def __init__(
        self,
        *,
        values_v: Iterable[float] = None,
        err_v: float = None,
        unit: str = None,
        values: Iterable[Qe] = None,
        symbol: sp.Symbol | str = None,
    ) -> None:
        if symbol is not None:
            self.symbol = generate_symbol(symbol)
        else:
            self.symbol = _create_unique_symbol()
        if values is not None:
            self.values = values
        elif values_v is not None:
            self.values = np.array(
                [
                    Qe(
                        value_v=value,
                        err_v=err_v,
                        unit=unit,
                        symbol=sp.Symbol(f"{self.symbol}_{i}"),
                    )
                    for i, value in enumerate(values_v)
                ]
            )
        else:
            raise ValueError("values not specified")
        if unit is not None:
            self.convert(unit)

    def convert(self, unit):
        for value in self.values:
            value.convert(unit)
