from enforce_typing import enforce_types

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
                               'time': 2,
                               'integration': 0.9,
                               'novelty': 0.9,
                               'impact': 9}
        self.RANDOM_BUYING = False
        self.PRIVATE_PUBLISH_COST: dict = {'data': 1, 'algo': 1, 'compute': 1} # arbitrary
        self.ASSET_COSTS: dict = {'private_market': {'data': 1, 'algo': 1, 'compute': 1}, 'public_market': {'data': 1, 'algo': 1, 'compute': 1}} # arbitrary



class SimState(SimStateBase.SimStateBase):
    def __init__(self):
        super().__init__()
        self.ss = SimStrategy()
        self.agents = AgentDict({})
        self.researchers: dict = {}
        self.public_researchers: dict = {}
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
    
    state.agents["public_market"] = SimpleKnowledgeMarketAgent("public_market", USD=0.0, OCEAN=0.0)
    state.agents["private_market"] = SimpleKnowledgeMarketAgent("private_market", USD=0.0, OCEAN=0.0)

    state.agents["dao"] = VersatileDAOTreasuryAgent(
                           "dao", USD=0.0, OCEAN=10.0)
    state.agents["r0"] = VersatileResearcherAgent("r0", USD=0.0, OCEAN=10.0, research_type='public', evaluator='dao', proposal_setup=state.ss.PROPOSAL_SETUP_0, receiving_agents={"market": 1.0})
    state.agents["r1"] = VersatileResearcherAgent("r1", USD=0.0, OCEAN=10.0, research_type='private', asset_type='algo', evaluator='dao', receiving_agents={"market": 1.0})
    state.researchers["r0"] = VersatileResearcherAgent("r0", USD=0.0, OCEAN=10.0, research_type='public', evaluator='dao', proposal_setup=state.ss.PROPOSAL_SETUP_0, receiving_agents={"market": 1.0})
    state.researchers["r1"] = VersatileResearcherAgent("r1", USD=0.0, OCEAN=10.0, research_type='private', asset_type='algo', evaluator='dao', receiving_agents={"market": 1.0})
    state.public_researchers["r0"] = VersatileResearcherAgent("r0", USD=0.0, OCEAN=10.0, research_type='public', evaluator='dao', proposal_setup=state.ss.PROPOSAL_SETUP_0, receiving_agents={"market": 1.0})
    
    r0 = state.agents["r0"]
    r1 = state.agents["r1"]
    dao = state.agents["dao"]
    m_pub = state.agents["public_market"]
    m_priv = state.agents["private_market"]
    
    # setup checks
    assert r0.OCEAN() and r1.OCEAN() == 10.0
    assert dao.OCEAN() == 10.0
    assert m_pub.OCEAN() == 0.0

    state.takeStep() # create just one proposal
    state.tick += 1 #tick = 1 #disperse here

    assert dao.proposal_evaluation == {}
    assert dao.update == 0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'integration': 0.9,
                               'novelty': 0.9,
                               'impact': 9,
                               'knowledge_access': 1.0}
                               
    assert r0.OCEAN() and r1.OCEAN() == 10.0

    # first funding
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1, 'integration': 0.9, 'novelty': 0.9, 'impact': 9}}
    assert dao.update == 1
    assert dao.OCEAN() == 9.0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'integration': 0.9,
                               'novelty': 0.9,
                               'impact': 9,
                               'knowledge_access': 1.0}
    assert r0.research_finished == False
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0

    # research takes place, nothing should happen
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1, 'integration': 0.9, 'novelty': 0.9, 'impact': 9}}
    assert dao.update == 0
    assert dao.OCEAN() == 9.0
    assert r0.research_finished == True
    assert r0.proposal == {}
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0

    # nothing happens, DAOTreasury sees that one proposal is not ready yet
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {}
    assert dao.update == 0
    assert dao.OCEAN() == 9.0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'integration': 0.9,
                               'novelty': 0.9,
                               'impact': 9,
                               'knowledge_access': 2.0}
    assert r0.research_finished == False
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0

    # second funding
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1, 'integration': 0.9, 'novelty': 0.9, 'impact': 9}}
    assert dao.update == 1
    assert dao.OCEAN() == 8.0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'integration': 0.9,
                               'novelty': 0.9,
                               'impact': 9,
                               'knowledge_access': 2.0}
    assert r0.research_finished == False
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 8.0

    state.takeStep()
    state.takeStep()
    # third funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 7.0
    state.takeStep()
    state.takeStep()
    # fourth funding
    state.takeStep()
    assert dao.OCEAN() == 6.0
    state.takeStep()
    state.takeStep()
    # fifth funding
    state.takeStep()
    assert dao.OCEAN() == 5.0
    state.takeStep()
    state.takeStep()
    # sixth funding
    state.takeStep()
    assert dao.OCEAN() == 4.0
    state.takeStep()
    state.takeStep()
    # seventh funding
    state.takeStep()
    assert dao.OCEAN() == 3.0
    state.takeStep()
    state.takeStep()
    # eighth funding
    state.takeStep()
    assert dao.OCEAN() == 2.0
    state.takeStep()
    state.takeStep()
    # ninth funding
    state.takeStep()
    assert dao.OCEAN() == 1.0
    state.takeStep()
    state.takeStep()
    # tenth funding
    state.takeStep()
    assert dao.OCEAN() == 0.0
    assert r1.OCEAN() == 7.0
    assert r0.knowledge_access == 11
    state.takeStep()
    state.takeStep()
    # eleventh funding will not take place
    state.takeStep()
    assert dao.proposal_evaluation == {}
    assert m_pub.OCEAN() + m_priv.OCEAN() == 13