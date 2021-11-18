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
    def __init__(self, name: str, evaluator: str, USD: float, OCEAN: float):
        super().__init__(name, USD, OCEAN)   
        self.generated_agents_idx = 0
        self._evaluator = evaluator
        
    def takeStep(self, state):
        if self._doCreateVersatileResearcherAgent(state):
            self._createVersatileResearcherAgent(state)

    def _doCreateVersatileResearcherAgent(self, state) -> bool:
        return state.getAgent(self._evaluator).update > 0

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