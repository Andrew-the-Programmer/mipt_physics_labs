# PHYSICAL CONSTANTS

from my_labs import PQ
from my_labs.my_physics.material_class import Material

_dencity: dict[str, PQ] = dict(
    oil=PQ(value=0.885, err=0.001, unit="g/cm^3", symbol="rho_oil"),
    water=PQ(value=1, err=0.1, unit="g/cm^3", symbol="rho_water"),
)

constants: dict[str, PQ | dict[str, PQ]] = dict(
    dencity=_dencity,
    g0=PQ(value=9.8, err=0, unit="m/s^2", symbol="g_0"),
    P0=PQ(value=1e5, err=0, unit="Pa", symbol="P_0"),
    R=PQ(value=8.314, err=0, unit="J/(mol*k)", symbol="R"),
)

materials: dict[str, Material] = dict(
    oil=Material(dencity=_dencity["oil"]),
    water=Material(dencity=_dencity["water"]),
)
