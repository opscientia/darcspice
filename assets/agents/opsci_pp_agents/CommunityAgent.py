import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import random

from engine.AgentBase import AgentBase
from util.constants import S_PER_MONTH

@enforce_types
class CommunityAgent(AgentBase):
    '''
    Participates in the knowledge market, integrates knowledge assets, receives rewards
    '''
    def __init__(self, name: str, USD: float, OCEAN: float):
        super().__init__(name, USD, OCEAN)

        #track amounts over time
        self.knowledge_access: int = 0
        self.curiosity: float = 1

    def takeStep(self, state) -> None:
        self.treasury = state.getAgent(state.ss.TREASURY)

        if self.treasury.update > 0:
            self._getCuriosity()
            if self.curiosity > 0.5 and self.OCEAN() >= 1000: # magic number
                self._interact(state)

    def _getCuriosity(self) -> None:
        assert self.treasury.proposal_evaluation != {}

        self.curiosity = (self.treasury.impact / 10) + random.uniform(-0.5, 0.5)
        if self.curiosity > 1:
            self.curiosity = 1
        if self.curiosity < 1:
            self.curiosity = 0

    def _interact(self, state):
        self._transferOCEAN(state.getAgent('public_market'), state.ss.PRICE_OF_ASSETS)
        self.knowledge_access += 1
        project = random.choice(state.projects.keys())
        state.projects[project].engagement += 1
        state.projects[project].impact += 1