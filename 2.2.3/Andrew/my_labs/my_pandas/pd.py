import pandas as pd
import numpy as np
import attr
from typing import Any, Iterable, Callable

from my_labs.vne import VNE, PQ
from my_labs.my_plt import SetXY


@attr.define()
class FrameSlice:
    columns: slice = attr.field(default=slice(None))
    rows: slice = attr.field(default=slice(None))
    
    def __init__(self, columns=None, rows=None):
        if columns is not None:
            self.columns = columns
        if rows is not None:
            self.rows = rows


def GetData(data: pd.DataFrame, frame_slice: FrameSlice) -> np.ndarray:
    return np.array(data.iloc[frame_slice.rows, frame_slice.columns])


def GetDataXY(
    data: pd.DataFrame,
    *,
    x_frame_slice: FrameSlice,
    y_frame_slice: FrameSlice,
    xerr_frame_slice: FrameSlice = None,
    yerr_frame_slice: FrameSlice = None,
    xerr=None,
    yerr=None,
    xkwargs: dict = None,
    ykwargs: dict = None,
    converter: type = PQ,
    kwargs: dict = None,
) -> SetXY:
    if xkwargs is None:
        xkwargs = dict()

    if ykwargs is None:
        ykwargs = dict()
    
    if kwargs is None:
        kwargs = dict()

    x = GetData(data, x_frame_slice)
    y = GetData(data, y_frame_slice)

    if xerr_frame_slice is not None:
        xerr = GetData(data, xerr_frame_slice)

    if yerr_frame_slice is not None:
        yerr = GetData(data, yerr_frame_slice)

    return SetXY(
        x=converter(value=x, err=xerr, **xkwargs),
        y=converter(value=y, err=yerr, **ykwargs),
        **kwargs,
    )


def WriteData(
    data: pd.DataFrame | Any, *, writer: pd.ExcelWriter | Any, **kwargs
) -> None:
    if not isinstance(data, pd.DataFrame):
        raise ValueError()
    data.to_excel(excel_writer=writer, **kwargs)


def SaveData(
    data: pd.DataFrame | Iterable[pd.DataFrame] | Any,
    *,
    file_path: Any,
    pos_func: Callable = None,
    **kwargs,
) -> None:
    with pd.ExcelWriter(file_path) as writer:
        if not isinstance(data, Iterable):
            WriteData(data, writer=writer, **kwargs)
            return
        startcol = 0
        startrow = kwargs.pop("startrow", 0)
        for i, d in enumerate(data):
            if pos_func is not None:
                startcol, startrow = pos_func(i)
            WriteData(d, writer=writer, startcol=startcol, startrow=startrow, **kwargs)
            startcol += d.shape[1] + 2
