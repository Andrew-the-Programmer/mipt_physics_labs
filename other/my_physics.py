import pandas as pd
import pathlib as pl
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import copy
import attr
import ipython_physics as phs

attr.define()
class ValueT:
    val: float = attr.field()
    err: float = attr.field()
    unit: str = attr.field()
    def eps(self):
        return self.val / self.err