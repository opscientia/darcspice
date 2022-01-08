import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
import random

from agents.opsci_pp_agents.VersatileResearcherAgent import VersatileResearcherAgent
from engine import AgentBase
                    
@enforce_types
class ResearcherGeneratorAgent(AgentBase.AgentBaseNoEvm):
    """Community growth agent"""
    def __init__(self, name: str, evaluator: str, USD: float, OCEAN: float, 
                 generator_cond_type: str, generator_type: str, time_interval: int, start_gen: int):
        super().__init__(name, USD, OCEAN)

        self.generated_agents_idx = 0
        self._evaluator = evaluator
        self.time_interval = time_interval
        self.market_update = 0
        self.generator_cond_type = generator_cond_type
        self.generator_type = generator_type
        self.last_generated = 0
        self.start_gen = start_gen

        # to track
        self.agents_generated = 0

        self.generate_cond = {"treasury": self._doCreateVersatileResearcherAgentTreasury, 
                         "market": self._doCreateVersatileResearcherAgentMarket,
                         "time": self._doCreateVersatileResearcherAgentTime}
        self.generate = {"linear": self._createLinVersatileResearcherAgent,
                         "exp": self._createExpVersatileResearcherAgent,
                         "dec": self._createDecVersatileResearcherAgent}

    def takeStep(self, state):

        if self.generate_cond[self.generator_cond_type](state):
            self.generate[self.generator_type](state)

    def _doCreateVersatileResearcherAgentTreasury(self, state) -> bool:
        return state.getAgent(self._evaluator).update > 0

    def _doCreateVersatileResearcherAgentMarket(self, state) -> bool:
        return (state.getAgent('public_market').total_knowledge_assets - self.market_update) >= 30 # magic number
    
    def _doCreateVersatileResearcherAgentTime(self, state) -> bool:
        return state.tick % self.time_interval == 0

    def _createLinVersatileResearcherAgent(self, state) -> None:
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
        self.agents_generated += 1
    
    def _createExpVersatileResearcherAgent(self, state) -> None:
        for i in range(self.last_generated + 1):
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
            self.agents_generated += 1
        self.last_generated += 1

    def _createDecVersatileResearcherAgent(self, state) -> None:
        if self.start_gen <= 1:
            return
        for i in range(self.start_gen):
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
            self.agents_generated += 1
        self.start_gen -= 1