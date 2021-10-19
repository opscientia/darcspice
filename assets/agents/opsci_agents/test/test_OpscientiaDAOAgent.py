from enforce_typing import enforce_types
import random

from assets.agents.opsci_agents.OpscientiaDAOAgent import OpscientiaDAOAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    pass

class SimState(SimStateBase.SimStateBase):
    pass

@enforce_types
def test1():
    ss = SimStrategy()
    assert hasattr(ss, 'time_step')
    ss.time_step = S_PER_DAY

    state = SimState(ss)

    class SimpleResearcherAgent(AgentBase.AgentBase):
        def __init__(self):
            self.proposal = None
        def createProposal(self) -> dict:
            return {'grant_requested': 1,
                    'assets_generated': 1,
                    'no_researchers': 1,
                    'knowledge_access': 1}
        def takeStep(self, state):
            self.proposal = self.createProposal()

    state.agents["a1"] = a1 = SimpleResearcherAgent("a1", 0.0, 0.0)
    assert a1.OCEAN() == 0.0

    dao1 = OpscientiaDAOAgent(
        "dao1", USD=0.0, OCEAN=1.0)
    assert dao1.OCEAN() == 1.0

    dao1.takeStep(state); state.tick += 1 #tick = 1 #disperse here
    assert dao1.OCEAN() == (1.0 - 1.0*1/4)
    assert a1.OCEAN() == (0.0 + 1.0*1/4)

    dao1.takeStep(state); state.tick += 1 #tick = 2
    assert dao1.OCEAN() == (1.0 - 1.0*1/4) 
    assert a1.OCEAN() == (0.0 + 1.0*1/4)

    dao1.takeStep(state); state.tick += 1 #tick = 3
    assert dao1.OCEAN() == (1.0 - 1.0*1/4)
    assert a1.OCEAN() == (0.0 + 1.0*1/4)

    dao1.takeStep(state); state.tick += 1 #tick = 4 #disperse here
    assert dao1.OCEAN() == (1.0 - 1.0*2/4) 
    assert a1.OCEAN() == (0.0 + 1.0*2/4)

    dao1.takeStep(state); state.tick += 1 #tick = 5
    assert dao1.OCEAN() == (1.0 - 1.0*2/4) 
    assert a1.OCEAN() == (0.0 + 1.0*2/4)

    dao1.takeStep(state); state.tick += 1 #tick = 6
    assert dao1.OCEAN() == (1.0 - 1.0*2/4) 
    assert a1.OCEAN() == (0.0 + 1.0*2/4)

    dao1.takeStep(state); state.tick += 1 #tick = 7 #disperse here
    assert dao1.OCEAN() == (1.0 - 1.0*3/4) 
    assert a1.OCEAN() == (0.0 + 1.0*3/4)

    dao1.takeStep(state); state.tick += 1 #tick = 8
    assert dao1.OCEAN() == (1.0 - 1.0*3/4)
    assert a1.OCEAN() == (0.0 + 1.0*3/4)

    dao1.takeStep(state); state.tick += 1 #tick = 9
    assert dao1.OCEAN() == (1.0 - 1.0*3/4)
    assert a1.OCEAN() == (0.0 + 1.0*3/4)

    dao1.takeStep(state); state.tick += 1 #tick = 10 #disperse here
    assert dao1.OCEAN() == (1.0 - 1.0*4/4) 
    assert a1.OCEAN() == (0.0 + 1.0*4/4)

    dao1.takeStep(state); state.tick += 1 #tick = 11
    dao1.takeStep(state); state.tick += 1 #tick = 12
    dao1.takeStep(state); state.tick += 1 #tick = 13 #don't disperse, 0 left

    assert dao1.OCEAN() == (1.0 - 1.0*4/4) 
    assert a1.OCEAN() == (0.0 + 1.0*4/4)
