from enforce_typing import enforce_types

from assets.agents.opsci_pp_agents.PrivateMarketAgent import PrivateKnowledgeMarketAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from engine.AgentDict import AgentDict
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        pass

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

    class SimpleDAOTreasury(AgentBase.AgentBase):
        def __init__(self, name: str,
                    USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
        def takeStep(self, state):
            pass

    class SimpleVersatileResearcherAgent(AgentBase.AgentBase):
        def __init__(self, name: str, research_type: str,
                    USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
            self.research_type: str = research_type
            self.asset_type: str = 'algo'
            self.total_OCEAN_spent_this_tick: float = 0.0

            self.proposal = {'assets_generated': 1.0}

        def _BuyAssets(self, state) -> None:
            self.ratio_funds_to_publish = 0.0 # not publishing
            if (self.OCEAN() != 0) and (self.OCEAN() >= 2) and (self.proposal != {}):
                OCEAN_DISBURSE =  2
                self.total_OCEAN_spent_this_tick += OCEAN_DISBURSE
                self.last_OCEAN_spent = {'tick': state.tick, 'spent': self.total_OCEAN_spent_this_tick, 'market': 'private_market', 'asset_buy': 'algo', 'publish': False, 'ratio': self.ratio_funds_to_publish}
                self._transferOCEAN(state.getAgent('private_market'), OCEAN_DISBURSE)

        def _BuyAndPublishAssets(self, state) -> None:
            self.ratio_funds_to_publish = 0.5
            if (self.OCEAN() != 0) and (self.OCEAN() >= 4) and (self.proposal != {}):
                OCEAN_DISBURSE =  4
                self.total_OCEAN_spent_this_tick += OCEAN_DISBURSE
                self.last_OCEAN_spent = {'tick': state.tick, 'spent': self.total_OCEAN_spent_this_tick, 'market': 'private_market', 'asset_buy': 'algo', 'publish': True, 'ratio': self.ratio_funds_to_publish, 'assets_generated': 1.0}
                self._transferOCEAN(state.getAgent('private_market'), OCEAN_DISBURSE)

        def takeStep(self, state) -> None:
            self.total_OCEAN_spent_this_tick = 0.0
            self.last_OCEAN_spent = {}
            if state.tick % 2 == 0:
                if self.research_type == 'private':
                    self._BuyAssets(state)
                else:
                    self._BuyAndPublishAssets(state)
    
    state.agents["dao"] = SimpleDAOTreasury("dao", USD=0.0, OCEAN=0.0)
    state.agents["r0"] = SimpleVersatileResearcherAgent("r0", research_type="private", USD=0.0, OCEAN=10.0)
    state.agents["r1"] = SimpleVersatileResearcherAgent("r1", research_type="public", USD=0.0, OCEAN=10.0)
    state.researchers["r0"] = SimpleVersatileResearcherAgent("r0", research_type="private", USD=0.0, OCEAN=10.0)
    state.researchers["r1"] = SimpleVersatileResearcherAgent("r1", research_type="public", USD=0.0, OCEAN=10.0)
    
    state.agents["private_market"] = PrivateKnowledgeMarketAgent("private_market", USD=0.0, OCEAN=0.0, transaction_fees_percentage=0.5, fee_receiving_agents={"dao": 1.0})
    r0 = state.agents["r0"]
    r1 = state.agents["r1"]
    dao = state.agents["dao"]
    m = state.agents["private_market"]
    
    # setup checks
    assert r0.OCEAN() and r1.OCEAN() == 10.0
    assert dao.OCEAN() == 0.0
    assert m.OCEAN() == 0.0

    state.takeStep() 
    state.tick += 1 #tick = 1 #disperse here

    assert state.tick == 1
    assert r0.OCEAN() == 8
    assert r1.OCEAN() == 8
    assert m.total_knowledge_assets == 1
    assert m.knowledge_assets == {'algo': 1.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 1.0}}
    assert m.OCEAN() == 1
    assert dao.OCEAN() == 3

    state.takeStep(); state.tick += 1
    assert state.tick == 2
    assert r0.OCEAN() == 8
    assert r1.OCEAN() == 8
    assert m.total_knowledge_assets == 1
    assert m.knowledge_assets == {'algo': 1.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 1.0}}
    assert m.OCEAN() == 1
    assert dao.OCEAN() == 3

    state.takeStep(); state.tick += 1
    assert state.tick == 3
    assert r0.OCEAN() == 6
    assert r1.OCEAN() == 6
    assert m.total_knowledge_assets == 2
    assert m.knowledge_assets == {'algo': 2.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 2.0}}
    assert m.OCEAN() == 2
    assert dao.OCEAN() == 6

    state.takeStep(); state.tick += 1
    assert state.tick == 4
    assert r0.OCEAN() == 6
    assert r1.OCEAN() == 6
    assert m.total_knowledge_assets == 2
    assert m.knowledge_assets == {'algo': 2.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 2.0}}
    assert m.OCEAN() == 2
    assert dao.OCEAN() == 6

    state.takeStep(); state.tick += 1
    assert state.tick == 5
    assert r0.OCEAN() == 4
    assert r1.OCEAN() == 4
    assert m.total_knowledge_assets == 3
    assert m.knowledge_assets == {'algo': 3.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 3.0}}
    assert m.OCEAN() == 3
    assert dao.OCEAN() == 9

    state.takeStep(); state.tick += 1
    assert state.tick == 6
    assert r0.OCEAN() == 4
    assert r1.OCEAN() == 4
    assert m.total_knowledge_assets == 3
    assert m.knowledge_assets == {'algo': 3.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 3.0}}
    assert m.OCEAN() == 3
    assert dao.OCEAN() == 9

    state.takeStep(); state.tick += 1
    assert state.tick == 7
    assert r0.OCEAN() == 2
    assert r1.OCEAN() == 2
    assert m.total_knowledge_assets == 4
    assert m.knowledge_assets == {'algo': 4.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 4.0}}
    assert m.OCEAN() == 4
    assert dao.OCEAN() == 12

    state.takeStep(); state.tick += 1
    assert state.tick == 8
    assert r0.OCEAN() == 2
    assert r1.OCEAN() == 2
    assert m.total_knowledge_assets == 4
    assert m.knowledge_assets == {'algo': 4.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 4.0}}
    assert m.OCEAN() == 4
    assert dao.OCEAN() == 12

    state.takeStep(); state.tick += 1
    assert state.tick == 9
    assert r0.OCEAN() == 0
    assert r1.OCEAN() == 3
    assert m.total_knowledge_assets == 4
    assert m.knowledge_assets == {'algo': 4.0}
    assert m.knowledge_assets_per_researcher == {'algo': {r1: 4.0}}
    assert m.OCEAN() == 4
    assert dao.OCEAN() == 13
    