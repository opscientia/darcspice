from enforce_typing import enforce_types
import math
from typing import List

from engine import KPIsBase
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, INF
from util.strutil import prettyBigNum

@enforce_types
class KPIs(KPIsBase.KPIsBase):
    def __init__(self,time_step: int):
        super().__init__(time_step)

        self._total_value_in_treasury: list = [0]
        self._total_value_in_rsrchs: list = [0]
        self._total_value_in_mrkts: list = [0]

        # relative values
        self._total_value_in_system: list = [0]
        self._relative_value_in_mrkts: list = [0]
        self._relative_value_in_rsrchrs: list = [0]
        self._relative_value_in_treasury: list = [0]

    def takeStep(self, state):
        super().takeStep(state)

        t, r, m = self._getTotalValues(state)

        self._total_value_in_treasury.append(t)
        self._total_value_in_rsrchs.append(r)
        self._relative_value_in_mrkts.append(m)

        system = t + r + m

        self._total_value_in_system.append(system)
        self._relative_value_in_mrkts.append(m / system)
        self._relative_value_in_rsrchrs.append(r / system)
        self._relative_value_in_treasury.append(t / system)

    def _getTotalValues(self, state):
        treasury_OCEAN = state.getAgent('dao_treasury').OCEAN()

        researcher_OCEAN = 0.0
        for r in state.researchers.keys():
            researcher_OCEAN += state.getAgent(r).OCEAN()
        markets_OCEAN = state.getAgent('market').OCEAN()

        return treasury_OCEAN, researcher_OCEAN, markets_OCEAN


@enforce_types
def netlist_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
    kpis = state.kpis
    s = [] #for console logging
    dataheader = [] # for csv logging: list of string
    datarow = [] #for csv logging: list of float

    r_dict = {}
    for r in state.researchers.keys():
        r_dict[r] = state.getAgent(r)
        s += ["; %s OCEAN=%s" % (r , prettyBigNum(r_dict[r].OCEAN(),False))]
        s += ["; %s proposals=%s" % (r, r_dict[r].no_proposals_submitted)]
        s += ["; %s proposals funded=%s" % (r, r_dict[r].no_proposals_funded)]
        dataheader += ["%s_knowledge_access" % r]
        datarow += [r_dict[r].knowledge_access]

        dataheader += ["%s_no_proposals" % r]
        datarow += [r_dict[r].no_proposals_submitted]

        dataheader += ["%s_no_proposals_funded" % r]
        datarow += [r_dict[r].no_proposals_funded]

        dataheader += ["%s_total_funding" % r]
        datarow += [r_dict[r].total_research_funds_received]

        dataheader += ["%s_total_assets_mrkt" % r]
        datarow += [r_dict[r].total_assets_in_mrkt]

        dataheader += ["%s_OCEAN" % r]
        datarow += [r_dict[r].my_OCEAN]

    treasury = state.getAgent("dao_treasury")
    s += ["; dao_treasury OCEAN=%s" % prettyBigNum(treasury.OCEAN(),False)]
    dataheader += ["dao_treasury_OCEAN"]
    datarow += [treasury.OCEAN()]

    dataheader += ["dao_treasury_funded_proposals_integration"]
    datarow += [treasury.integration]

    dataheader += ["dao_treasury_funded_proposals_novelty"]
    datarow += [treasury.novelty]
    dataheader += ["dao_treasury_funded_proposals_in_index"]
    datarow += [treasury.in_index]
    dataheader += ["funded_proposals_impact"]
    datarow += [treasury.impact]

    staker = state.getAgent("staker")
    s += ["; staker OCEAN=%s" % prettyBigNum(staker.OCEAN(),False)]
    dataheader += ["staker_OCEAN"]
    datarow += [staker.OCEAN()]

    market = state.getAgent("market")
    s += ["; market OCEAN=%s" % prettyBigNum(market.OCEAN(),False)]
    dataheader += ["market_OCEAN"]
    datarow += [market.OCEAN()]
    dataheader += ["market_fees_OCEAN"]
    datarow += [market.total_fees]

    dataheader += ["market_assets"]
    datarow += [market.total_knowledge_assets]

    dataheader += ["total_value_in_treasury"]
    datarow += [kpis._total_value_in_treasury[-1]]
    dataheader += ["total_value_in_researchers"]
    datarow += [kpis._total_value_in_rsrchs[-1]]
    dataheader += ["total_value_in_markets"]
    datarow += [kpis._total_value_in_mrkts[-1]]

    dataheader += ["total_value_of_system"]
    datarow += [kpis._total_value_in_system[-1]]
    dataheader += ["relative_value_in_markets"]
    datarow += [kpis._relative_value_in_mrkts[-1]]
    dataheader += ["relative_value_in_researchers"]
    datarow += [kpis._relative_value_in_rsrchrs[-1]]
    dataheader += ["relative_value_in_treasury"]
    datarow += [kpis._relative_value_in_treasury[-1]]


    #done
    return s, dataheader, datarow

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
    r_list = [e for e in header if 'researcher' in e]
    proposals = [p for p in r_list if 'proposals' in p[-9:]]
    proposals_funded = [p for p in r_list if '_no_proposals_funded' in p]
    knowledge_access = [k for k in r_list if 'knowledge_access' in k]
    total_funding = [t for t in r_list if '_total_funding' in t]
    total_OCEAN = [o for o in r_list if '_OCEAN' in o]
    total_assets_mrkt = [m for m in r_list if 'total_assets_mrkt' in m]
    researchers = []
    i = [i for i in range(0, 200)]
    for idx in i:
        for r in r_list:
            if ('researcher%x' % idx) in r:
                if ('researcher%x' % idx) not in researchers:
                    researchers.append('researcher%x' % idx)
    researchers.reverse()
    
    y_params = [
        YParam(["total_value_in_treasury", "total_value_in_researchers", "total_value_in_markets"],
        ["treasury", "researchers", "markets"],"Value distribution in the system",LINEAR,MULT1,COUNT),
        YParam(["total_value_of_system"],
        [""],"Total value in the system",LINEAR,MULT1,COUNT),
        YParam(["relative_value_in_markets", "relative_value_in_researchers", "relative_value_in_treasury"],
        ["markets", "researchers", "treasury"],"Relative value distribution in the system",LINEAR,MULT1,COUNT),
        YParam(proposals_funded,
        researchers,"#_proposals_FUNDED",LINEAR,MULT1,COUNT),
        YParam(["dao_treasury_funded_proposals_integration", "dao_treasury_funded_proposals_novelty", "dao_treasury_funded_proposals_in_index"],
        ["integration", "novelty", "in_index"],"integration vs novelty in funded proposals",LINEAR,MULT1,COUNT),
        YParam(["funded_proposals_impact"],["impact"], "impact of funded proposals",LINEAR,MULT1,COUNT),
        YParam(proposals,
        researchers,"#_proposals",LINEAR,MULT1,COUNT),
        YParam(total_funding,
        researchers,"OCEAN funding",LINEAR,MULT1,COUNT),
        YParam(total_assets_mrkt,
        researchers,"Assets in Knowledge Market",LINEAR,MULT1,COUNT),
        YParam(knowledge_access,
        researchers,"Knowledge access index",LINEAR,MULT1,COUNT),
        YParam(total_OCEAN,
        researchers,"Researcher OCEAN",LINEAR,MULT1,COUNT),
        YParam(["dao_treasury_OCEAN"],
        ["dao_treasury"],"DAO_Treasury_OCEAN",LINEAR,MULT1,COUNT),
        YParam(["staker_OCEAN", "market_OCEAN"],
        ["staker", "market"],"Staker_X_KnowledgeMarket_OCEAN",LOG,MULT1,COUNT),
        YParam(["staker_OCEAN", "market_fees_OCEAN"],
        ["staker", "market"],"Staker_OCEAN_vs_total_Fees",LINEAR,MULT1,COUNT),
    ]

    return (x, y_params)
