import logging
from enforce_typing import enforce_types
import random
from typing import List
import math

from assets.agents.PoolAgent import PoolAgent
from engine.AgentBase import AgentBase
from web3engine import bpool, datatoken, globaltokens
from web3tools.web3util import fromBase18, toBase18
from util import constants
log = logging.getLogger('agents')

@enforce_types
class ResearcherAgent(AgentBase):
    '''
    So far only a combination of DataconsumerAgent and GrantTakingAgent
    '''   
    def __init__(self, name: str, USD: float, OCEAN: float, 
                 receiving_agents : dict):
        super().__init__(name, USD, OCEAN)
        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent
        self._receiving_agents = receiving_agents

        self.proposal = None
        # self._s_since_buy = 0 # seconds since bought data
        # self._s_between_buys = 3 * constants.S_PER_DAY  # magic number
        # self.profit_margin_on_consume = 0.2  # magic number
    
    def createProposal(self) -> dict:
        return {'grant_requested': random.randint(1000, 50000),
                'no_researchers': random.randint(1, 10),
                'research_length_mo': random.randint(1, 24),
                'assets_generated': random.randint(1, 10)}  

    def spentAtTick(self) -> float:
        return self._spent_at_tick

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)
    
    def takeStep(self, state):
        if self.proposal == None:  
            self.proposal = self.createProposal()  
        self._spent_at_tick = self.USD() + self.OCEAN() * state.OCEANprice()

        if self.USD() > 0:
            self._disburseUSD(state)
        if self.OCEAN() > 0:
            self._disburseOCEAN(state)
        
        # Once all funds have been spent, research is done and new proposal can be submitted
        if self.OCEAN() == 0 and self.USD() == 0:
            self.proposal = None
        # self._s_since_buy += state.ss.time_step
