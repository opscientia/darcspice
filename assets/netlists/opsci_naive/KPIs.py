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

    researcher0 = state.getAgent("researcher0")
    s += ["; researcher0 USD=%s" % prettyBigNum(researcher0.USD(),False)]
    s += ["; researcher0 proposals=%s" % (researcher0.no_proposals_submitted,)]
    s += ["; researcher0 proposals funded=%s" % (researcher0.no_proposals_funded,)]
    dataheader += ["researcher0_knowledge_access"]
    datarow += [researcher0.knowledge_access]

    dataheader += ["researcher0_no_proposals"]
    datarow += [researcher0.no_proposals_submitted]

    dataheader += ["researcher0_no_proposals_funded"]
    datarow += [researcher0.no_proposals_funded]

    dataheader += ["researcher0_total_funding"]
    datarow += [researcher0.total_research_funds_received]


    researcher1 = state.getAgent("researcher1")
    s += ["; researcher1 USD=%s" % prettyBigNum(researcher1.USD(),False)]
    s += ["; researcher1 proposals=%s" % (researcher1.no_proposals_submitted,)]
    s += ["; researcher1 proposals funded=%s" % (researcher1.no_proposals_funded,)]
    dataheader += ["researcher1_knowledge_access"]
    datarow += [researcher1.knowledge_access]

    dataheader += ["researcher1_no_proposals"]
    datarow += [researcher1.no_proposals_submitted]

    dataheader += ["researcher1_no_proposals_funded"]
    datarow += [researcher1.no_proposals_funded]

    dataheader += ["researcher1_total_funding"]
    datarow += [researcher1.total_research_funds_received]

    uni = state.getAgent("university")
    s += ["; university OCEAN=%s" % prettyBigNum(uni.OCEAN(),False)]
    dataheader += ["university_OCEAN"]
    datarow += [uni.OCEAN()]

    sellers = state.getAgent("sellers")
    s += ["; sellers OCEAN=%s" % prettyBigNum(sellers.OCEAN(),False)]
    dataheader += ["sellers_OCEAN"]
    datarow += [sellers.OCEAN()]

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
        YParam(["researcher0_no_proposals_funded","researcher1_no_proposals_funded"],
        ["researcher0","researcher1"],"number of proposals funded",LINEAR,MULT1,COUNT),
        YParam(["researcher0_no_proposals","researcher1_no_proposals"],
        ["researcher0","researcher1"],"number of proposals",LINEAR,MULT1,COUNT),
        YParam(["researcher0_total_funding","researcher1_total_funding"],
        ["researcher0","researcher1"],"OCEAN funding",LINEAR,MULT1,COUNT),
        YParam(["researcher0_knowledge_access","researcher1_knowledge_access"],
        ["researcher0","researcher1"],"Knowledge access index",LINEAR,MULT1,COUNT),
        YParam(["university_OCEAN"],
        ["university"],"University OCEAN",LINEAR,MULT1,COUNT),

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

@enforce_types
def netlist_rp_createLogData(state):
    """pass this to SimEngine.__init__() as argument `netlist_createLogData`"""
    kpis = state.kpis
    dataheader = [] # for csv logging: list of string
    datarow = [] #for csv logging: list of float

    return dataheader, datarow

@enforce_types
def netlist_rp_plotInstructions(header: List[str], values):
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
