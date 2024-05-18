""" :3 """

import logging
from typing import Iterable, Any
import sympy as sp

from my_labs.vne import VNE
from my_labs.my_time import TimeIt
from my_labs.my_sp import Substitute, GetSymbol, GetErrSymbol


__all__ = ["Substitute", "calculate", "converted", "scaled", "negative"]


def _split_subs(subs: dict[sp.Symbol, VNE]) -> tuple[dict]:
    logging.debug(f"_split_subs:\n{subs=}\n")
    single_subs: dict[sp.Symbol, VNE] = dict()
    range_subs: dict[sp.Symbol, VNE] = dict()
    for key, value in subs.items():
        (range_subs if value.is_range() else single_subs)[key] = value
    return single_subs, range_subs


def _rearrange_subs(range_subs: dict[sp.Symbol, VNE]):
    logging.debug(f"_rearrange_subs:\n{range_subs=}\n")
    return [
        dict(zip(range_subs.keys(), v))
        for v in zip(*[ve.get_list() for ve in range_subs.values()])
    ]


def _rearrange_and_split_subs(subs: dict[sp.Symbol, VNE]):
    logging.debug(f"_rearrange_and_split_subs:\n{subs=}\n")
    return [_split_subs(sub) for sub in _rearrange_subs(subs)]


def _transformed_subs(subs: dict[Any, Any]) -> dict[sp.Symbol, VNE]:
    logging.debug("_transformed_subs:")
    return {GetSymbol(key): VNE(value) for key, value in subs.items()}


def calculate_value_r(
    equation,
    *,
    single_subs: dict[sp.Symbol, VNE] = None,
    range_subs: dict[sp.Symbol, VNE] = None,
):
    logging.debug(f"calculate_value_r:\n{equation=}\n{single_subs=}\n{range_subs=}\n")
    equation = Substitute(equation, dict((k, v.value) for k, v in single_subs.items()))
    if not range_subs:
        return equation
    return [
        calculate_value_r(equation, single_subs=ssubs, range_subs=rsubs)
        for ssubs, rsubs in _rearrange_and_split_subs(range_subs)
    ]


def calculate_value_s(equation, subs: dict[sp.Symbol, VNE]):
    logging.debug(f"calculate_value_s:\n{equation=}\n{subs=}\n")
    single_subs, range_subs = _split_subs(subs)
    logging.debug(f"\n{single_subs=}\n{range_subs=}\n")
    return calculate_value_r(equation, single_subs=single_subs, range_subs=range_subs)


def calculate_value(equation, subs: dict):
    logging.debug(f"calculate_value:\n{equation=}\n{subs=}\n")
    return calculate_value_s(equation, subs=_transformed_subs(subs))


def get_err_equation(equation, symbols: Iterable[sp.Symbol]):
    return sp.sqrt(
        sum(
            [
                sp.diff(equation, symbol) ** 2 * GetErrSymbol(symbol) ** 2
                for symbol in symbols
            ]
        )
    )


def calculate_err_s(equation, subs: dict[sp.Symbol, VNE]):
    logging.debug(f"calculate_err_s:\n{equation=}\n{subs=}\n")
    err_eq = get_err_equation(equation, subs.keys())
    logging.debug(f"{err_eq=}")
    err_subs: dict[sp.Symbol, VNE] = dict()
    for symbol in subs.keys():
        err_subs[GetErrSymbol(symbol)] = VNE(subs[symbol].err)
    logging.debug(f"{err_subs=}")
    return calculate_value_s(err_eq, err_subs | subs)


def calculate_err(equation, subs: dict):
    logging.debug(f"calculate_err:\n{equation=}\n{subs=}\n")
    return calculate_value(equation, _transformed_subs(subs))


def calculate(equation, subs: dict[sp.Symbol | str, Any]) -> Any:
    logging.debug(f"calculate:\n{equation=}\n{subs=}\n")
    tsubs = _transformed_subs(subs)
    value = calculate_value_s(equation, tsubs)
    err = calculate_err_s(equation, tsubs)
    return VNE(value=value, err=err)


def converted(
    value: Any,
    equation,
    *,
    subs: dict[sp.Symbol | str, Any] = None,
    symbol: sp.Symbol = sp.Symbol("x"),
) -> VNE:
    """equation should contain <symbol>"""
    if subs is None:
        subs = dict()
    return calculate(equation, subs=subs | {symbol: value})


def scaled(*, scale: Any, value: Any) -> VNE:
    return converted(value, equation=sp.Symbol("x") * scale, symbol="x")

def negative(value: Any) -> VNE:
    return scaled(value=value, scale=-1)
