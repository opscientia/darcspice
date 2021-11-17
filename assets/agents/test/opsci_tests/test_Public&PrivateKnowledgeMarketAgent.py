from enforce_typing import enforce_types

from assets.agents.opsci_pp_agents.PrivateMarketAgent import PrivateKnowledgeMarketAgent
from assets.agents.opsci_pp_agents.PublicMarketAgent import PublicKnowledgeMarketAgent
from assets.agents.opsci_pp_agents.VersatileDAOTreasuryAgent import VersatileDAOTreasuryAgent
from assets.agents.opsci_pp_agents.VersatileResearcherAgent import VersatileResearcherAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from engine.AgentDict import AgentDict
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        self.PROPOSALS_FUNDED_AT_A_TIME = 1
        self.PRICE_OF_ASSETS = 1
        self.FUNDING_BOUNDARY = 0
        self.RATIO_FUNDS_TO_PUBLISH = 0
        self.PROPOSAL_SETUP_0 = {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2}
        self.PROPOSAL_SETUP_1 = {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2}
        self.RANDOM_BUYING = False
        self.TREASURY = 'dao_treasury'
        self.PRIVATE_PUBLISH_COST: dict = {'data': 20000, 'algo': 20000, 'compute': 30000} # arbitrary
        self.ASSET_COSTS: dict = {'private_market': {'data': 20000, 'algo': 20000, 'compute': 30000}, 'public_market': {'data': 1000, 'algo': 1000, 'compute': 2000}} # arbitrary


class SimState(SimStateBase.SimStateBase):
    def __init__(self):
        super().__init__()
        self.ss = SimStrategy()
        self.agents = AgentDict({})
        self.researchers: dict = {}
        self.public_researchers: dict = {}
        self.private_researchers: dict = {}
    def takeStep(self) -> None:
        for agent in list(self.agents.values()):
            agent.takeStep(self)

@enforce_types
def test1():
    state = SimState()

    class SimpleKnowledgeMarketAgent(AgentBase.AgentBase):
        def __init__(self, name: str, USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
        def takeStep(self, state) -> None:
            pass
    
    state.agents["market"] = SimpleKnowledgeMarketAgent("market", USD=0.0, OCEAN=0.0)

    state.agents["dao"] = MultTimeDAOTreasuryAgent(
                           "dao", USD=0.0, OCEAN=10.0)
    state.agents["r0"] = MultTimeResearcherAgent("r0", "dao", USD=0.0, OCEAN=10.0, proposal_setup=state.ss.PROPOSAL_SETUP_0, receiving_agents={"market": 1.0})
    state.agents["r1"] = MultTimeResearcherAgent("r1", "dao", USD=0.0, OCEAN=10.0, proposal_setup=state.ss.PROPOSAL_SETUP_1, receiving_agents={"market": 1.0})
    state.researchers["r0"] = MultTimeResearcherAgent("r0", "dao", USD=0.0, OCEAN=10.0, proposal_setup=state.ss.PROPOSAL_SETUP_0, receiving_agents={"market": 1.0})
    state.researchers["r1"] = MultTimeResearcherAgent("r1", "dao", USD=0.0, OCEAN=10.0, proposal_setup=state.ss.PROPOSAL_SETUP_1, receiving_agents={"market": 1.0})
    
    r0 = state.agents["r0"]
    r1 = state.agents["r1"]
    dao = state.agents["dao"]
    m = state.agents["market"]
    
    # setup checks
    assert r0.OCEAN() and r1.OCEAN() == 10.0
    assert dao.OCEAN() == 10.0
    assert m.OCEAN() == 0.0

    state.takeStep() # create just one proposal
    state.tick += 1 #tick = 1 #disperse here

    assert dao.proposal_evaluation == {}
    assert dao.update == 0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 1}
    assert r1.proposal == {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 1}
    assert r0.OCEAN() and r1.OCEAN() == 10.0
    assert m.OCEAN() == 0.0