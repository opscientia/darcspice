from enforce_typing import enforce_types

from assets.agents.opsci_agents.profit_sharing_agents.OpscientiaDAOAgent import OpscientiaDAOAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from engine.AgentDict import AgentDict
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        self.TICKS_BETWEEN_PROPOSALS = 1
        self.FUNDING_BOUNDARY = 0

class SimState(SimStateBase.SimStateBase):
    def __init__(self):
        super().__init__()
        self.ss = SimStrategy()
        self.agents = AgentDict({})
        self.researchers: dict = {}
    def takeStep(self) -> None:
        for agent in list(self.agents.values()):
            agent.takeStep()

@enforce_types
def test1():
    state = SimState()

    class SimpleResearcherAgent(AgentBase.AgentBase):
        def __init__(self, name: str, USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
            self.proposal: dict = {}
        def createProposal(self) -> dict:
            return {'grant_requested': 1,
                    'assets_generated': 1,
                    'no_researchers': 1,
                    'knowledge_access': 1}
        def takeStep(self):
            self.proposal = self.createProposal()

    state.agents["a1"] = SimpleResearcherAgent("a1", 0.0, 0.0)
    state.researchers['a1']  = SimpleResearcherAgent("a1", 0.0, 0.0)
    a1 = state.agents['a1']
    assert a1.OCEAN() == 0.0

    dao1 = OpscientiaDAOAgent(
        "dao1", USD=0.0, OCEAN=10.0)
    assert dao1.OCEAN() == 10.0

    state.takeStep() # create just one proposal
    assert a1.proposal is not None
    dao1.takeStep(state); state.tick += 1 #tick = 1 #disperse here
    assert dao1.OCEAN() == 9.0
    assert a1.OCEAN() == 1.0

    dao1.takeStep(state); state.tick += 1 #tick = 2 #disperse here
    assert dao1.OCEAN() == 8.0
    assert a1.OCEAN() == 2.0

    dao1.takeStep(state); state.tick += 1 #tick = 3 #disperse here
    assert dao1.OCEAN() == 7.0
    assert a1.OCEAN() == 3.0

    dao1.takeStep(state); state.tick += 1 #tick = 4 #disperse here
    assert dao1.OCEAN() == 6.0
    assert a1.OCEAN() == 4.0

    dao1.takeStep(state); state.tick += 1 #tick = 5 #disperse here
    assert dao1.OCEAN() == 5.0
    assert a1.OCEAN() == 5.0

    dao1.takeStep(state); state.tick += 1 #tick = 6 #disperse here
    assert dao1.OCEAN() == 4.0
    assert a1.OCEAN() == 6.0

    dao1.takeStep(state); state.tick += 1 #tick = 7 #disperse here
    assert dao1.OCEAN() == 3.0
    assert a1.OCEAN() == 7.0

    dao1.takeStep(state); state.tick += 1 #tick = 8 #disperse here
    assert dao1.OCEAN() == 2.0
    assert a1.OCEAN() == 8.0

    dao1.takeStep(state); state.tick += 1 #tick = 9 #disperse here
    assert dao1.OCEAN() == 1.0
    assert a1.OCEAN() == 9.0

    dao1.takeStep(state); state.tick += 1 #tick = 10 #disperse here
    assert dao1.OCEAN() == 0.0
    assert a1.OCEAN() == 10.0

    dao1.takeStep(state); state.tick += 1 #tick = 11 #don't disperse, 0 left

    assert dao1.OCEAN() == 0.0
    assert a1.OCEAN() == 10.0
