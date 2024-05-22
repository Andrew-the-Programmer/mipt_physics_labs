from typing import Literal
import attr

from my_labs.vne import PQ


@attr.define()
class Line:
    slope: PQ = attr.field()
    intercept: PQ = attr.field()

    def __init__(
        self,
        *,
        slope=None,
        intercept=None,
    ) -> None:
        if slope is None:
            self.slope = PQ(symbol='alpha')
        else:
            self.slope = slope

        if intercept is None:
            self.intercept = PQ(symbol='beta')
        else:
            self.intercept = intercept

    def equation_repr(
        self,
        *,
        repr_type: Literal["condensed", "absolute", "fsdp"] = "fsdp",
        config: dict = None,
        **kwargs,
    ) -> str:
        return f"y = ({self.slope.repr(repr_type=repr_type, config=config, **kwargs)}) x + ({self.intercept.repr(repr_type=repr_type, config=config, **kwargs)})"

    def repr(
        self,
        *,
        repr_type: Literal["equation"] = "equation",
        config: dict = None,
        **kwargs,
    ) -> str:
        if repr_type == "equation":
            return self.equation_repr(config=config, **kwargs)
        raise ValueError(f"repr_type={repr_type} is not supported")
