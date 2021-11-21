import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
import random

from assets.agents.opsci_pp_agents.VersatileResearcherAgent import VersatileResearcherAgent
from engine.AgentBase import AgentBase
from web3tools.web3util import toBase18
                    
@enforce_types
class ResearcherGeneratorAgent(AgentBase):
    """Community growth agent"""
    def __init__(self, name: str, evaluator: str, USD: float, OCEAN: float, generator_type: str, time_interval: int):
        super().__init__(name, USD, OCEAN)

        self.generated_agents_idx = 0
        self._evaluator = evaluator
        self.time_interval = time_interval
        self.market_update = 0
        self.generator_type = generator_type

    def takeStep(self, state):

        if self.generator_type == "treasury":
            if self._doCreateVersatileResearcherAgentTreasury(state):
                self._createVersatileResearcherAgent(state)
        elif self.generator_type == "market":
            if self._doCreateVersatileResearcherAgentMarket(state):
                self._createVersatileResearcherAgent(state)
        elif self.generator_type == "time":
            if self._doCreateVersatileResearcherAgentTime(state):
                self._createVersatileResearcherAgent(state)



    def _doCreateVersatileResearcherAgentTreasury(self, state) -> bool:
        return state.getAgent(self._evaluator).update > 0

    def _doCreateVersatileResearcherAgentMarket(self, state) -> bool:
        return (state.getAgent('public_market').total_knowledge_assets - self.market_update) >= 10
    
    def _doCreateVersatileResearcherAgentTime(self, state) -> bool:
        return state.tick % self.time_interval == 0

    def _createVersatileResearcherAgent(self, state) -> None:
        name = f'new_researcher_{self.generated_agents_idx}'
        self.generated_agents_idx += 1
        USD = 0.0 # magic number
        OCEAN = 200000.0 # same as other researchers
        new_agent = VersatileResearcherAgent(name=name, USD=USD, OCEAN=OCEAN, 
                                            evaluator = "dao_treasury",
                                            research_type='private',
                                            receiving_agents = {"market": 1.0})
        state.addAgent(new_agent)
        state.addResearcherAgent(new_agent)