import logging
from typing import Iterable, Any
import sympy as sp

from VNE import VNE
from my_time import TimeIt


def GetSymbol(value):
    if isinstance(value, str):
        return sp.Symbol(value)
    if isinstance(value, sp.Symbol):
        return value
    else:
        raise ValueError("Invalid value type")


def _get_err_symbol(symbol) -> sp.Symbol:
    return GetSymbol(f"_err_{symbol}")


def _split_subs(subs: dict[sp.Symbol, VNE]) -> tuple[dict]:
    single_subs: dict[sp.Symbol, VNE] = dict()
    range_subs: dict[sp.Symbol, VNE] = dict()
    for key, value in subs.items():
        (range_subs if value.is_range() else single_subs)[key] = value
    return single_subs, range_subs


def _rearrange_subs(range_subs: dict[sp.Symbol, VNE]):
    return [
        dict(zip(range_subs.keys(), v))
        for v in zip(*[ve.get_list() for ve in range_subs.values()])
    ]


def _rearrange_and_split_subs(subs: dict[sp.Symbol, VNE]):
    logging.debug(f"{_rearrange_subs(subs)=}")
    return [_split_subs(sub) for sub in _rearrange_subs(subs)]


def _transformed_subs(subs: dict[Any, Any]) -> dict[sp.Symbol, VNE]:
    return {GetSymbol(key): VNE(value) for key, value in subs.items()}


def calculate_value_r(
    equation,
    *,
    single_subs: dict[sp.Symbol, VNE] = None,
    range_subs: dict[sp.Symbol, VNE] = None,
):
    equation = sp.simplify(equation)
    logging.debug(f"calculate_value_r:\n{equation=}\n{single_subs=}\n{range_subs=}")
    equation = equation.evalf(subs=dict((k, v.value) for k, v in single_subs.items()))
    equation = sp.simplify(equation)
    if not range_subs:
        return equation
    return [
        calculate_value_r(equation, single_subs=ssubs, range_subs=rsubs)
        for ssubs, rsubs in _rearrange_and_split_subs(range_subs)
    ]


def calculate_value_s(equation, subs: dict[sp.Symbol, VNE]):
    logging.debug(f"calculate_value_s: {equation=}\n{subs=}")
    single_subs, range_subs = _split_subs(subs)
    logging.debug(f"{single_subs=}, {range_subs=}")
    return calculate_value_r(equation, single_subs=single_subs, range_subs=range_subs)


def calculate_value(equation, subs: dict):
    logging.debug(f"calculate_value: {equation=}\n{subs=}")
    return calculate_value_s(equation, subs=_transformed_subs(subs))


def get_err_equation(equation, symbols: Iterable[sp.Symbol]):
    return sp.sqrt(
        sum(
            [
                sp.diff(equation, symbol) ** 2 * _get_err_symbol(symbol) ** 2
                for symbol in symbols
            ]
        )
    )


def calculate_err_s(equation, subs: dict[sp.Symbol, VNE]):
    logging.debug(f"calculate_err_s: {equation=}\n{subs=}")
    err_eq = get_err_equation(equation, subs.keys())
    logging.debug(f"{err_eq=}")
    err_subs: dict[sp.Symbol, VNE] = dict()
    for symbol in subs.keys():
        err_subs[_get_err_symbol(symbol)] = VNE(subs[symbol].err)
    logging.debug(f"{err_subs=}")
    return calculate_value_s(err_eq, err_subs | subs)


def calculate_err(equation, subs: dict):
    logging.debug(f"calculate_err: {equation=}\n{subs=}")
    return calculate_value(equation, _transformed_subs(subs))


@TimeIt
def calculate(equation, subs: dict[sp.Symbol]) -> Any:
    logging.debug(f"calculate: {equation=}\n{subs=}")
    tsubs = _transformed_subs(subs)
    value = TimeIt(calculate_value_s)(equation, tsubs)
    err = TimeIt(calculate_err_s)(equation, tsubs)
    return VNE((value, err))


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    x, y, z = sp.symbols("x y z")
    # eq = 3 * x**2 + sp.sin(y * sp.exp(z)) * x * y
    eq = x + y + z
    subs = {x: [(1, 0.5), (2, 1), (30, 15)], y: (2, 1), z: [4, 5, 100]}
    print(calculate(eq, subs))

    print(eq)


if __name__ == "__main__":
    main()
