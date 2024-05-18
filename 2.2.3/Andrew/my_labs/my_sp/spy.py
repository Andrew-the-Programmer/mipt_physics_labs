""" :3 """

from typing import Any
import sympy as sp


def Substitute(equation: sp.Eq, subs: dict[str | sp.Symbol, Any]) -> Any:
    return equation.subs(subs).evalf()


def GetSymbol(value) -> sp.Symbol:
    if isinstance(value, str):
        return sp.Symbol(value)
    if isinstance(value, sp.Symbol):
        return value
    else:
        raise ValueError("Invalid value type")


def GetErrSymbol(symbol) -> sp.Symbol:
    return GetSymbol(f"_err_{symbol}")
