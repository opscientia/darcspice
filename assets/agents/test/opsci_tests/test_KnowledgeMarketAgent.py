from enforce_typing import enforce_types

from assets.agents.opsci_agents.profit_sharing_agents.KnowledgeMarketAgent import KnowledgeMarketAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from engine.AgentDict import AgentDict
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        self.TICKS_BETWEEN_PROPOSALS = 2
        self.TREASURY = 't'

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

    class SimpleResearcherAgent(AgentBase.AgentBase):
        def __init__(self, name: str, USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
            self.proposal = None
            self.last_tick_spent = 0
            self.proposal = {'assets_generated': 1}
            self.ratio_funds_to_publish: float = 0.0

        def _BuyAndPublishAssets(self, state) -> None:
            self.ratio_funds_to_publish = 0.5
            self._transferOCEAN(state.getAgent('market'), 4)

        def _BuyAssets(self, state) -> None:
            self.ratio_funds_to_publish = 0.0
            self._transferOCEAN(state.getAgent('market'), 4)

        def takeStep(self, state) -> None:
            self.last_tick_spent = state.tick
            if self.OCEAN() > 4:
                if (state.tick % state.ss.TICKS_BETWEEN_PROPOSALS) == 0:
                    self._BuyAndPublishAssets(state)
                else:
                    self._BuyAssets(state)
    
    class SimpleTreasuryAgent(AgentBase.AgentBase):
        def __init__(self, name: str, USD: float, OCEAN: float):
            super().__init__(name, USD, OCEAN)
            self.proposal_evaluation = {'winner': 'r'}
        def takeStep(self, state):
            pass

    state.agents['t']  = SimpleTreasuryAgent("t", 0.0, 0.0)
    state.agents['r'] = SimpleResearcherAgent("r", USD=0.0, OCEAN=10.0)
    state.researchers['r'] = SimpleResearcherAgent("r", USD=0.0, OCEAN=10.0)
    state.agents['market'] = KnowledgeMarketAgent(
        "market", USD=0.0, OCEAN=0.0, transaction_fees_percentage=0.25, 
        fee_receiving_agents={'t': 1.0})
    m = state.agents['market']
    r = state.agents['r']
    t = state.agents['t']

    assert m.OCEAN() == 0.0
    assert t.proposal_evaluation == {'winner': 'r'}
    assert r.OCEAN() == 10.0


    state.takeStep(); state.tick += 1 # tick 1, researcher publishes
    assert state.tick == 1
    assert m.total_knowledge_assets == 1
    assert r.OCEAN() == 6
    assert m.OCEAN() == 3
    assert t.OCEAN() == 1

    state.takeStep(); state.tick += 1 # tick 2, researcher buys
    assert state.tick == 2
    assert m.total_knowledge_assets == 1
    assert r.OCEAN() == 5
    assert m.OCEAN() == 3
    assert t.OCEAN() == 2

    state.takeStep(); state.tick += 1 # tick 3, researcher publishes
    assert state.tick == 3
    assert m.total_knowledge_assets == 2
    assert r.OCEAN() == 2.5
    assert m.OCEAN() == 4.5
    assert t.OCEAN() == 3

    