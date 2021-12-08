from enforce_typing import enforce_types
import math
from typing import List
from tqdm import tqdm

from engine import KPIsBase
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, INF
from util.strutil import prettyBigNum

@enforce_types
class RKPIs(KPIsBase.KPIsBase):
    def __init__(self,time_step: int):
        super().__init__(time_step)

        self._total_rp: list = [0]
        self._total_rp_engagement: list = [0]
        self._total_rp_value: list = [0]
        self._total_rp_impact: list = [0]
        self._total_rp_integration: list = [0]
        self._total_rp_novelty: list = [0]

    def takeStep(self, state):
        super().takeStep(state)
        self._getProjectValues(state)

    def _getProjectValues(self, state) -> None:
        projects = state.projects
        self._total_rp.append(len(projects.keys()))
        self._total_rp_engagement.append(sum(project.engagement for project in projects.values()))
        self._total_rp_value.append(sum(project.value for project in projects.values()))
        self._total_rp_integration.append(sum(project.integration for project in projects.values()))
        self._total_rp_novelty.append(sum(project.novelty for project in projects.values()))
        self._total_rp_impact.append(sum(project.impact for project in projects.values()))

@enforce_types
def netlist_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
    rkpis = state.rkpis
    dataheader = [] # for csv logging: list of string
    datarow = [] #for csv logging: list of float

    dataheader += ["total_rp"]
    datarow += [rkpis._total_rp[-1]]
    dataheader += ["total_rp_engagement"]
    datarow += [rkpis._total_rp_engagement[-1]]
    dataheader += ["total_rp_integration"]
    datarow += [rkpis._total_rp_integration[-1]]
    dataheader += ["total_rp_novelty"]
    datarow += [rkpis._total_rp_novelty[-1]]
    dataheader += ["total_rp_impact"]
    datarow += [rkpis._total_rp_impact[-1]]

    for rp, spec in state.projects.keys():
        dataheader += ["%s_impact" % rp]
        datarow += [spec.impact]
        dataheader += ["%s_engagement" % rp]
        datarow += [spec.engagement]

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
    rp_list = [e for e in header if 'rp' in e]
    impact = [p for p in rp_list if '_impact' in p]
    engagement = [p for p in rp_list if '_engagement' in p]
    
    y_params = [
        YParam(["total_rp"],
        ["total"],"Total projects funded",LINEAR,MULT1,COUNT),
        YParam(["total_rp_engagement"],
        ["total"],"Total project engagement",LINEAR,MULT1,COUNT),
        YParam(["total_rp_integration"],
        ["total"],"Total project integration",LINEAR,MULT1,COUNT),
        YParam(["total_rp_novelty"],
        ["total"],"Total project novelty",LINEAR,MULT1,COUNT),
        YParam(["total_rp_impact"],
        ["total"],"Total project impact",LINEAR,MULT1,COUNT),
        YParam(impact,
        impact,"Research projects impact",LINEAR,MULT1,COUNT),
        YParam(engagement,
        engagement,"Research projects engagement",LINEAR,MULT1,COUNT),
    ]

    return (x, y_params)
