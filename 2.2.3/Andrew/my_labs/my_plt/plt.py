from typing import Any, Iterable
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

from my_labs.vne import PQ
from .setxy_class import SetXY
from .line_class import Line


def find_trendline(xyset: SetXY) -> Line:
    line = linregress(x=np.array(xyset.x.value), y=np.array(xyset.y.value))
    return Line(
        slope=PQ(value=line.slope, err=line.stderr, unit=xyset.y.unit / xyset.x.unit),
        intercept=PQ(
            value=line.intercept, err=line.intercept_stderr, unit=xyset.x.unit
        ),
    )


def add_trendline(xyset: SetXY, plot_config: dict = None, repr_config: dict = None):
    tl: Line = find_trendline(xyset)
    if repr_config is None:
        repr_config = dict()
    if plot_config is None:
        plot_config = dict(label=tl.repr(**repr_config))
    y = np.array(xyset.x.value) * tl.slope.value + tl.intercept.value
    plt.plot(
        xyset.x.value,
        y,
        **plot_config,
    )


def plot_xyset(xyset: SetXY, *, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            linestyle="",
            # fmt=".",
        )
    plt.errorbar(
        x=xyset.x.value,
        y=xyset.y.value,
        xerr=xyset.x.err,
        yerr=xyset.y.err,
        **config | kwargs,
    )


def add_figure(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            figsize=(10, 6),  # размером 16 на 9 дюймов
            facecolor="whitesmoke",  # c подложкой цвета белый дым
            dpi=100,  # разрешением 200 точек
        )
    plt.figure(
        **config | kwargs,
    )


def add_title(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            label="<title>",
            fontsize=20,
        )
    plt.title(
        **config | kwargs,
    )


def add_xlabel(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            xlabel="<xlabel>",
            fontsize=20,
        )
    plt.xlabel(
        **config | kwargs,
    )


def add_ylabel(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            ylabel="<ylabel>",
            fontsize=20,
        )
    plt.ylabel(
        **config | kwargs,
    )


def add_legend(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            loc="lower right",
            borderaxespad=1,
        )
    plt.legend(
        **config | kwargs,
    )


def add_grid(*, config: dict = None, **kwargs):
    if config is None:
        config = dict(
            visible=True,
            which="major",
            axis="both",
        )
    plt.grid(
        **config | kwargs,
    )


def savefigure(*, filename: Any, config: dict = None, **kwargs) -> None:
    if config is None:
        config = dict(
            bbox_inches="tight",
            pad_inches=0.1,
        )
    plt.savefig(
        filename,
        **config | kwargs,
    )


def Plot(
    xyset: SetXY,
    *,
    plot_config: dict = None,
    figure_config: dict = None,
    plot_trendline: bool = True,
    trendline_config: dict = None,
    trendline_repr_config: dict = None,
    title_config: dict = None,
    title: str = None,
    xlabel_config: dict = None,
    xlabel: str = None,
    ylabel_config: dict = None,
    ylabel: str = None,
    legend_config: dict = None,
    grid_config: dict = None,
    savefig: Any = None,
    savefig_config: dict = None,
    close: bool = False,
) -> None:
    if title is None:
        title = xyset.title

    if xlabel is None:
        xlabel = xyset.x.get_label()

    if ylabel is None:
        ylabel = xyset.y.get_label()

    add_figure(config=figure_config)
    plot_xyset(xyset, config=plot_config)

    if plot_trendline:
        add_trendline(
            xyset, plot_config=trendline_config, repr_config=trendline_repr_config
        )

    add_title(config=title_config, label=title)

    add_xlabel(config=xlabel_config, xlabel=xlabel)
    add_ylabel(config=ylabel_config, ylabel=ylabel)

    add_legend(config=legend_config)
    add_grid(config=grid_config)

    if savefig is not None:
        savefigure(filename=savefig, config=savefig_config)

    # plt.show()
    if close:
        plt.close()


def PlotDataSet(
    dataset: Iterable[SetXY],
    *,
    kwargs,
):
    for d in dataset:
        plot_xyset(d.as_numeric(), **kwargs)
