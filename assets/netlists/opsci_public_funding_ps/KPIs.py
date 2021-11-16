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
    for r in state.public_researchers.keys():
        r_dict[r] = state.getAgent(r)
        s += ["; %s OCEAN=%s" % (r , prettyBigNum(r_dict[r].OCEAN(),False))]
        s += ["; %s proposals=%s" % (r, r_dict[r].no_proposals_submitted)]
        s += ["; %s proposals funded=%s" % (r, r_dict[r].no_proposals_funded)]
        s += ["; research type=%s; asset type=%s" % (r_dict[r].research_type, r_dict[r].asset_type)]
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

        dataheader += ["%s_public_OCEAN" % r]
        datarow += [r_dict[r].my_OCEAN]
    
    for r in state.private_researchers.keys():
        r_dict[r] = state.getAgent(r)
        s += ["; %s OCEAN=%s" % (r , prettyBigNum(r_dict[r].OCEAN(),False))]
        s += ["; %s proposals=%s" % (r, r_dict[r].no_proposals_submitted)]
        s += ["; %s proposals funded=%s" % (r, r_dict[r].no_proposals_funded)]
        s += ["; research type=%s; asset type=%s" % (r_dict[r].research_type, r_dict[r].asset_type)]

        dataheader += ["%s_total_assets_mrkt" % r]
        datarow += [r_dict[r].total_assets_in_mrkt]

        dataheader += ["%s_private_OCEAN" % r]
        datarow += [r_dict[r].my_OCEAN]

    treasury = state.getAgent("dao_treasury")
    s += ["; dao_treasury OCEAN=%s" % prettyBigNum(treasury.OCEAN(),False)]
    dataheader += ["dao_treasury_OCEAN"]
    datarow += [treasury.OCEAN()]

    private_market = state.getAgent("private_market")
    s += ["; private_market OCEAN=%s" % prettyBigNum(private_market.OCEAN(),False)]
    dataheader += ["private_market_OCEAN"]
    datarow += [private_market.OCEAN()]
    dataheader += ["private_market_fees_OCEAN"]
    datarow += [private_market.total_fees]

    dataheader += ["private_market_assets"]
    datarow += [private_market.total_knowledge_assets]

    # if private_market.knowledge_assets != {}:
    #     for type, count in private_market.knowledge_assets.items():
    #         dataheader += ["private_market_%s" % type]
    #         datarow += [count]

    public_market = state.getAgent("public_market")
    s += ["; public_market OCEAN=%s" % prettyBigNum(public_market.OCEAN(),False)]
    dataheader += ["public_market_OCEAN"]
    datarow += [public_market.OCEAN()]
    dataheader += ["public_market_fees_OCEAN"]
    datarow += [public_market.total_fees]

    dataheader += ["public_market_assets"]
    datarow += [public_market.total_knowledge_assets]


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
    total_public_OCEAN = [o for o in r_list if '_public_OCEAN' in o]
    total_private_OCEAN = [o for o in r_list if '_private_OCEAN' in o]
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
        # YParam(['private_market_data', 'private_market_algo', 'private_market_compute'], ['private_market'], "Private Market Knowledge Assets (by type)" ,LINEAR,MULT1,COUNT),

        YParam(proposals_funded,
        researchers,"#_proposals_FUNDED",LINEAR,MULT1,COUNT),
        YParam(proposals,
        researchers,"#_proposals",LINEAR,MULT1,COUNT),
        YParam(total_funding,
        researchers,"OCEAN funding",LINEAR,MULT1,COUNT),
        YParam(total_assets_mrkt,
        researchers,"Assets in Knowledge Market",LINEAR,MULT1,COUNT),
        YParam(knowledge_access,
        researchers,"Knowledge access index",LINEAR,MULT1,COUNT),
        YParam(total_public_OCEAN,
        researchers,"Researcher OCEAN",LINEAR,MULT1,COUNT),
        YParam(total_private_OCEAN,
        researchers,"Researcher OCEAN",LINEAR,MULT1,COUNT),
        YParam(["dao_treasury_OCEAN"],
        ["dao_treasury"],"DAO_Treasury_OCEAN",LINEAR,MULT1,COUNT),
        YParam(["private_market_OCEAN", "public_market_OCEAN"],
        ["private_market", "public_market"],"Private vs Public Market OCEAN",LOG,MULT1,COUNT),
        YParam(["private_market_fees_OCEAN", "public_market_fees_OCEAN"],
        ["private_market", "public_market"],"Total fees collected through private vs public market",LINEAR,MULT1,COUNT),
    ]

    return (x, y_params)
