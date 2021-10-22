from enforce_typing import enforce_types
import math
from typing import List

from engine import KPIsBase
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, INF
from util.strutil import prettyBigNum

@enforce_types
class KPIs(KPIsBase.KPIsBase):
    pass


@enforce_types
def netlist_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
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

    staker = state.getAgent("staker")
    s += ["; staker OCEAN=%s" % prettyBigNum(staker.OCEAN(),False)]
    dataheader += ["staker_OCEAN"]
    datarow += [staker.OCEAN()]

    market = state.getAgent("market")
    s += ["; market OCEAN=%s" % prettyBigNum(market.OCEAN(),False)]
    dataheader += ["market_OCEAN"]
    datarow += [market.OCEAN()]

    dataheader += ["market_assets"]
    datarow += [market.total_knowledge_assets]

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
    
    y_params = [
        YParam(["researcher0_no_proposals_funded","researcher1_no_proposals_funded", "researcher2_no_proposals_funded"],
        ["researcher0","researcher1", "researcher2"],"#_proposals_FUNDED",LINEAR,MULT1,COUNT),
        YParam(["researcher0_no_proposals","researcher1_no_proposals"],
        ["researcher0","researcher1"],"#_proposals",LINEAR,MULT1,COUNT),
        YParam(["researcher0_total_funding","researcher1_total_funding"],
        ["researcher0","researcher1"],"OCEAN funding",LINEAR,MULT1,COUNT),
        YParam(["researcher0_total_assets_mrkt","researcher1_total_assets_mrkt"],
        ["researcher0","researcher1"],"Assets in Knowledge Market",LINEAR,MULT1,COUNT),
        YParam(["researcher0_knowledge_access","researcher1_knowledge_access", "researcher2_knowledge_access"],
        ["researcher0","researcher1", "researcher2"],"Knowledge access index",LINEAR,MULT1,COUNT),
        YParam(["researcher0_OCEAN","researcher1_OCEAN", "researcher2_OCEAN"],
        ["researcher0","researcher1", "researcher2"],"Researcher OCEAN",LINEAR,MULT1,COUNT),
        YParam(["dao_treasury_OCEAN"],
        ["dao_treasury"],"DAO_Treasury_OCEAN",LINEAR,MULT1,COUNT),
        YParam(["staker_OCEAN", "market_OCEAN"],
        ["staker", "market"],"Staker_X_KnowledgeMarket_OCEAN",LOG,MULT1,COUNT),
        YParam(["staker_OCEAN"],
        ["staker"],"Staker_OCEAN",LINEAR,MULT1,COUNT),
        # YParam(["OCEAN_price"], [""], "OCEAN Price", LOG, MULT1, DOLLAR),
        # #YParam(["ocean_rev_growth/yr"], [""], "Annual Ocean Revenue Growth", BOTH, MULT100, PERCENT),
        # YParam(["overall_valuation", "fundamentals_valuation","speculation_valuation"],
        #       ["Overall", "Fundamentals (P/S=30)", "Speculation"], "Valuation", LOG, DIV1M, DOLLAR),
        # YParam(["dao_USD/mo", "dao_OCEAN_in_USD/mo", "dao_total_in_USD/mo"],
        #       ["Income as USD (ie network revenue)", "Income as OCEAN (ie from 51%; priced in USD)", "Total Income"],
        #       "Monthly OpscientiaDAO Income", LOG, DIV1M, DOLLAR),
        # YParam(["ocean_rev/yr","allSellers_rev/yr"], ["Ocean", "All sellers"],
        #       "Annual Revenue", LOG, DIV1M, DOLLAR),
        # YParam(["tot_OCEAN_supply", "tot_OCEAN_minted", "tot_OCEAN_burned"],
        #       ["Total supply","Tot # Minted","Tot # Burned"], "OCEAN Token Count", BOTH, DIV1M, COUNT),
        # YParam(["OCEAN_minted/mo", "OCEAN_burned/mo"], ["# Minted/mo", "# Burned/mo"],
        #       "Monthly # OCEAN Minted & Burned", BOTH, DIV1M, COUNT),
        
        # YParam(["OCEAN_burned_USD/mo", "OCEAN_minted_USD/mo"],
        #        ["$ of OCEAN Burned/mo", "$ of OCEAN Minted/mo"],
        #       "Monthly OCEAN (in USD) Minted & Burned", LOG, DIV1M, DOLLAR),
        # YParam(["OCEAN_burned_USD/mo", "ocean_rev/mo", "allSellers_rev/mo"],
        #       ["$ OCEAN Burned monthly", "Ocean monthly revenue", "Sellers monthly revenue"],
        #       "Monthly OCEAN Burned & Seller Revenues", LOG, DIV1M, DOLLAR),
    ]

    return (x, y_params)
