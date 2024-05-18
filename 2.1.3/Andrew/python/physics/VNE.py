import attr
from typing import Any, Iterable
from typing_extensions import Self


# type spNumericType = int|float
# type CalculatableType = NumericType|Iterable[NumericType]


@attr.define()
class ValueAndError:
    value: Any = attr.field()
    err: Any = attr.field(default=0)

    def __init__(self, any_value: Any=None, *, value=None, err=None) -> None:
        if value is not None:
            self.value = value
        if err is not None:
            self.err = err
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
            vnes: list[ValueAndError] = [ValueAndError(v) for v in any_value]
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
            raise ValueError('self must represent a range')
        if self._err_is_range():
            return [ValueAndError((value, err)) for value, err in zip(self.value, self.err)]
        return [ValueAndError((value, self.err)) for value in self.value]

    def eps(self):
        return self.err / self.value

    def condensed_repr(self, notation: str = "") -> str:
        return f"{self.value :{notation}} +- {self.err :{notation}}"

    def __str__(self):
        return self.condensed_repr()

    def __repr__(self):
        return str(self)

VNE = ValueAndError
