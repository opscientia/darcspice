from enforce_typing import enforce_types

from assets.agents.opsci_agents.MultTimeDAOTreasuryAgent import MultTimeDAOTreasuryAgent
from assets.agents.opsci_agents.MultTimeResearcherAgent import MultTimeResearcherAgent
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


class SimState(SimStateBase.SimStateBase):
    def __init__(self):
        super().__init__()
        self.ss = SimStrategy()
        self.agents = AgentDict({})
        self.researchers: dict = {}
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

    # first funding
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1}}
    assert dao.update == 1
    assert dao.OCEAN() == 9.0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 1}
    assert r0.research_finished == False
    assert r1.proposal == {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 2}
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0
    assert m.OCEAN() == 2.0

    # research takes place, nothing should happen
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1}}
    assert dao.update == 0
    assert dao.OCEAN() == 9.0
    assert r0.research_finished == True
    assert r0.proposal == None
    assert r1.proposal == {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 2}
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0
    assert m.OCEAN() == 2.0

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
                               'knowledge_access': 2}
    assert r0.research_finished == False
    assert r1.proposal == {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 2}
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 9.0
    assert m.OCEAN() == 2.0

    # second funding
    state.takeStep()
    state.tick += 1
    assert dao.proposal_evaluation == {0: {'winner': 'r0', 'amount': 1}}
    assert dao.update == 1
    assert dao.OCEAN() == 8.0
    assert r0.proposal == {'grant_requested': 1,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 2}
    assert r0.research_finished == False
    assert r1.proposal == {'grant_requested': 2,
                               'assets_generated': 1,
                               'no_researchers': 10,
                               'time': 2,
                               'knowledge_access': 3}
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 8.0
    assert m.OCEAN() == 4.0

    state.takeStep()
    state.takeStep()
    # third funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 7.0
    state.takeStep()
    state.takeStep()
    # fourth funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 6.0
    state.takeStep()
    state.takeStep()
    # fifth funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 5.0
    state.takeStep()
    state.takeStep()
    # sixth funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 4.0
    state.takeStep()
    state.takeStep()
    # seventh funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 3.0
    state.takeStep()
    state.takeStep()
    # eighth funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 2.0
    state.takeStep()
    state.takeStep()
    # ninth funding
    state.takeStep()
    assert dao.OCEAN() and r1.OCEAN() == 1.0
    state.takeStep()
    state.takeStep()
    # tenth funding
    state.takeStep()
    assert dao.OCEAN() == 0.0
    assert r1.OCEAN() == 0.0
    assert r1.knowledge_access == 11
    assert r0.knowledge_access == 11
    state.takeStep()
    state.takeStep()
    # eleventh funding will not take place
    state.takeStep()
    assert dao.proposal_evaluation == {}
    assert r1.knowledge_access == r0.knowledge_access
    assert m.OCEAN() == 20.0



