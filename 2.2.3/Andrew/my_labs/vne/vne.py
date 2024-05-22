import logging
from copy import copy
from typing import Any, Iterable, Literal
import attr
from typing_extensions import Self
import numpy as np
import sympy as sp

from my_labs.my_numbers import convert_to_numeric_type, fsdp, medium


__all__ = ["VNE", "ValueAndError"]


def _value_repr(value: Any, config: dict[str, str] = None, **kwargs) -> str:
    if config is None:
        config = dict()

    if isinstance(value, str):
        return value

    if isinstance(value, Iterable):
        conf: dict[str, str] = (
            {
                "begin": "[",
                "end": "]",
                "sep": ", ",
                "notation": "",
            }
            | config
            | kwargs
        )
        begin = conf.pop("begin")
        end = conf.pop("end")
        sep = conf.pop("sep")
        return begin + sep.join([_value_repr(v, config=conf) for v in value]) + end

    conf: dict[str, str] = (
        {
            "begin": "",
            "end": "",
            "notation": "",
        }
        | config
        | kwargs
    )
    return conf["begin"] + f"{value:{conf['notation']}}" + conf["end"]


@attr.define()
class ValueAndError:
    value: Any = attr.field()
    err: Any = attr.field()

    def __init__(self, any_value: Any = None, *, value=None, err=None) -> None:
        if value is not None:
            if err is None:
                err = 0
            ValueAndError.__init__(self, (value, err))
            return
        try:
            self.value = any_value.get_value()
            self.err = any_value.get_err()
            return
        except AttributeError:
            pass
        if isinstance(any_value, ValueAndError):
            self.value = any_value.value
            self.err = any_value.err
        elif isinstance(any_value, tuple):
            if len(any_value) == 2:
                self.value = any_value[0]
                self.err = any_value[1]
            else:
                raise ValueError(
                    "get_value: if value is tuple, it must have 2 elements: (value, err)"
                )
        elif isinstance(any_value, Iterable):
            vnes: Iterable[ValueAndError] = np.array(
                [ValueAndError(v) for v in any_value]
            )
            self.value = [vne.value for vne in vnes]
            self.err = [vne.err for vne in vnes]
        else:
            self.value = any_value
            self.err = 0

    def _value_is_range(self) -> bool:
        return isinstance(self.value, Iterable)

    def _err_is_range(self) -> bool:
        return isinstance(self.err, Iterable)

    def is_range(self) -> bool:
        return self._value_is_range()

    def get_list(self) -> list[Self]:
        if not self.is_range():
            raise ValueError("self must represent a range")
        if self._err_is_range():
            return [
                ValueAndError((value, err)) for value, err in zip(self.value, self.err)
            ]
        return [ValueAndError((value, self.err)) for value in self.value]

    def eps(self):
        return self.err / self.value

    def repr_condensed(
        self,
        *,
        config: dict[str, str] = None,
        value_repr_config: dict[str, str] = None,
        err_repr_config: dict[str, str] = None,
    ) -> str:
        if self._value_is_range() and self._err_is_range():
            return _value_repr(
                [
                    v.repr_condensed(
                        config=config,
                        value_repr_config=value_repr_config,
                        err_repr_config=err_repr_config,
                    )
                    for v in self.get_list()
                ],
                config=config,
            )

        if config is None:
            config = dict()

        conf: dict[str, str] = {
            "begin": "",
            "end": "",
            "sep": " +- ",
        } | config

        return (
            conf["begin"]
            + _value_repr(self.value, config=value_repr_config)
            + conf["sep"]
            + _value_repr(self.err, config=err_repr_config)
            + conf["end"]
        )

    def repr_fsdp(
        self,
        *,
        config: dict[str, str] = None,
        value_repr_config: dict[str, str] = None,
        err_repr_config: dict[str, str] = None,
        extra_digits: int = 0,
    ) -> str:
        dp = max(fsdp(self.value), fsdp(self.err)) + extra_digits
        # print(f"VNE::repr_fsdp: {dp=}")

        if value_repr_config is None:
            value_repr_config = dict()
        if err_repr_config is None:
            err_repr_config = dict()

        n = {"notation": f".{dp}f"}

        return self.repr_condensed(
            config=config,
            value_repr_config=n | value_repr_config,
            err_repr_config=n | err_repr_config,
        )

    def repr(
        self,
        *args,
        repr_type: Literal["condensed", "fsdp"] = "condensed",
        **kwargs,
    ) -> str:
        """fsdp - first substantial decimal place"""

        if repr_type == "condensed":
            return self.repr_condensed(*args, **kwargs)
        if repr_type == "fsdp":
            return self.repr_fsdp(*args, **kwargs)
        raise ValueError(f"repr_type={repr_type} is not supported")

    def __str__(self):
        return self.repr_condensed()

    def __repr__(self):
        return str(self)

    def medium(self) -> Self:
        if not self.is_range():
            raise ValueError("self must represent a range")
        return ValueAndError(value=medium(self.value), err=medium(self.err))

    def as_numeric(self):
        result = copy(self)
        result.value = convert_to_numeric_type(self.value)
        result.err = convert_to_numeric_type(self.err)
        return result

    def __getitem__(self, index):
        return self.get_list()[index]


VNE = ValueAndError
