from enforce_typing import enforce_types
import math
from typing import List
from tqdm import tqdm

from engine import KPIsBase
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, INF
from util.strutil import prettyBigNum

@enforce_types
class KPIs(KPIsBase.KPIsBase):
    def __init__(self,time_step: int):
        super().__init__(time_step)


    def takeStep(self, state):
        super().takeStep(state)

@enforce_types
def netlist_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
    kpis = state.kpis
    s = [] #for console logging
    dataheader = [] # for csv logging: list of string
    datarow = [] #for csv logging: list of float

@enforce_types
def netlist_plotInstructions(header: List[str], values):
    """
    Describe how to plot the information.
    tsp.do_plot() calls this

    :param: header: List[str] holding 'Tick', 'Second', ...
    :param: values: 2d array of float [tick_i, valuetype_i]
    :return: x: List[float] -- x-axis info on how to plot
    :return: y_params: List[YParam] -- y-axis info on how to plot
    """
    from util.plotutil import YParam, arrayToFloatList, \
        LINEAR, LOG, BOTH, \
        MULT1, MULT100, DIV1M, DIV1B, \
        COUNT, DOLLAR, PERCENT
    
    x = arrayToFloatList(values[:,header.index("Month")])
    
    y_params = [
    ]

    return (x, y_params)
