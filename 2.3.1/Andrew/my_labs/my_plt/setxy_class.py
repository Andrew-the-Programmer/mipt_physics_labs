from copy import copy
from typing import Any
from typing_extensions import Self
import attr
import sympy as sp
import pandas as pd

from my_labs.vne import PQ, Unit
from my_labs.calculate import converted, negative
from my_labs.my_sp import GetSymbol


@attr.define()
class SetXY:
    x: PQ = attr.field()
    y: PQ = attr.field()
    title: str = attr.field(default="<title>")

    def __init__(
        self,
        *,
        title: str = "<title>",
        x=None,
        y=None,
        xsymbol="x",
        ysymbol="y",
        xkwargs: dict = None,
        ykwargs: dict = None,
    ) -> None:
        self.title = title

        if x is None:
            self.set_x(symbol=xsymbol, **xkwargs)
        else:
            self.x = x

        if y is None:
            self.set_y(symbol=ysymbol, **ykwargs)
        else:
            self.y = y

        if self.x.symbol is None:
            self.x.set_symbol("x")

        if self.y.symbol is None:
            self.y.set_symbol("y")

    def set_x(self, *args, value=None, err=None, symbol="x", **kwargs):
        self.x = PQ(*args, value=value, err=err, symbol=symbol, **kwargs)

    def set_y(self, *args, value=None, err=None, symbol="y", **kwargs):
        self.y = PQ(*args, value=value, err=err, symbol=symbol, **kwargs)

    def converted(
        self,
        *,
        xequation=None,
        yequation=None,
        xsubs: dict[sp.Symbol, Any] = None,
        ysubs: dict[sp.Symbol, Any] = None,
        inherit_symbol: bool = True,
        keep_unit: bool = False,
    ) -> Self:
        result = copy(self)
        if xequation is not None:
            result.set_x(
                converted(self.x, equation=xequation, subs=xsubs, symbol=self.x.symbol),
                symbol=xequation if inherit_symbol else self.x.symbol,
                unit=self.x.unit if keep_unit else Unit(None),
            )
        if yequation is not None:
            result.set_y(
                converted(self.y, equation=yequation, subs=ysubs, symbol=self.y.symbol),
                symbol=yequation if inherit_symbol else self.y.symbol,
                unit=self.y.unit if keep_unit else Unit(None),
            )
        return result

    def as_numeric(self):
        return SetXY(x=self.x.as_numeric(), y=self.y.as_numeric())

    def move(
        self, *, dx=None, dy=None, dx_symbol=None, dy_symbol=None, **kwargs
    ) -> Self:
        if dx_symbol is None:
            dx_symbol = GetSymbol(f"__d__{self.x.symbol}")

        if dy_symbol is None:
            dy_symbol = GetSymbol(f"__d__{self.y.symbol}")

        if dx is None:
            xequation = None
            xsubs = None
        else:
            xequation = self.x.symbol + dx_symbol
            xsubs = {dx_symbol: dx}

        if dy is None:
            yequation = None
            ysubs = None
        else:
            yequation = self.y.symbol + dy_symbol
            ysubs = {dy_symbol: dy}

        kwargs.setdefault("inherit_symbol", False)
        kwargs.setdefault("keep_unit", True)

        return self.converted(
            xequation=xequation,
            yequation=yequation,
            xsubs=xsubs,
            ysubs=ysubs,
            **kwargs,
        )

    def move_x_to_0(self, **kwargs) -> Self:
        return self.move(dx=negative(self.x[0]), **kwargs)

    def move_y_to_0(self, **kwargs):
        return self.move(dy=negative(self.y[0]), **kwargs)

    def get_table(self) -> pd.DataFrame:
        result = pd.DataFrame()
        result[self.x.get_label()] = self.x.value
        result[self.y.get_label()] = self.y.value
        return result
