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
    ResearcherAgent publishes proposals, creates knowledge assets and publishes them to a knowledge curator.
    Also, it keeps track of the following metrics:
    - number of proposals submitted
    - number of proposals funded
    - total funds received for research
    '''   
    def __init__(self, name: str, USD: float, OCEAN: float,
                 no_researchers: int, receiving_agents : dict):
        super().__init__(name, USD, OCEAN)
        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent
        self._receiving_agents = receiving_agents
        self.no_researchers = no_researchers

        self.proposal = None
        self.knowledge_access: float = 0.0
        self.ticks_since_proposal: int = 0
        self.proposal_accepted = False
        self.tick_of_proposal = 0

        # metrics to track
        self.no_proposals_submitted: int = 0
        self.no_proposals_funded: int = 0
        self.total_research_funds_received: float = 0.0

        self.TICKS_BETWEEN_PROPOSALS = 6480 # 1tick = 1hour and a research project in this simulation lasts 9 months, so 9*30*24=6480
    
    def createProposal(self, state) -> dict:
        self.tick_of_proposal = state.tick
        return {'grant_requested': random.randint(10000, 50000), # Note: might be worth considering some distribution based on other params
                'assets_generated': random.randint(1, 10), # Note: might be worth considering some distribution based on other params 
                'no_researchers': self.no_researchers,
                'knowledge_access': self.knowledge_access}

    def spentAtTick(self) -> float:
        return self._spent_at_tick

    def _USDToDisbursePerTick(self, state) -> None:
        '''
        1 tick = 1 hour
        '''
        if self.proposal != None:
            no_ticks = constants.S_PER_DAY / 3600
            disburse_per_tick = self.proposal['grant_requested'] / no_ticks
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * disburse_per_tick)
    
    def _OCEANToDisbursePerTick(self, state) -> None:
        '''
        1 tick = 1 hour
        '''
        OCEAN = self.OCEAN()
        if OCEAN != 0:
            OCEAN_DISBURSE = OCEAN / 5 # arbitrary number so that researchers don't spend everything at once
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN_DISBURSE)
    
    def takeStep(self, state):

        # Proposal functionality: one problem is that the agent that evaluates proposals and gives grants is often
        # the first one to takeStep, when there are no proposals yet.
        if self.proposal is None:
            self.proposal = self.createProposal(state)
            self.no_proposals_submitted += 1

        # checking to see whether it is time to submit a new proposal
        # POSSIBLE ERROR: both ResearcherAgent instances need to be aligned (not sure if that's going to work) 
        # AND it's also possible that there will be misalignment with the OpscientiaDAOAgent (grant giving agent in this case)
        if (self.ticks_since_proposal % self.TICKS_BETWEEN_PROPOSALS) == 0:
            self.proposal = self.createProposal(state)
            self.no_proposals_submitted += 1
        
        # Checking if proposal accepted (should only be checked at the tick right after the tick when createProposal() was called)
        if state.tick - self.tick_of_proposal == 1:
            if state.getAgent('university').proposal_evaluation['winner'] == self.name:
                self.proposal_accepted = True
                self.no_proposals_funded += 1
            # In case the funding is misaligned with the researchers
            elif state.getAgent('university').proposal_evaluation['winner'] == None:
                self.tick_of_proposal = state.tick
            elif state.getAgent('university').proposal_evaluation['winner'] != self.name:
                self.proposal_accepted = False
        
        
        
        if self.proposal_accepted:
            self.ticks_since_proposal += 1
        
        # self._spent_at_tick = self.USD() + self.OCEAN() * state.OCEANprice()
        self._spent_at_tick = self.OCEAN()

        if self.USD() > 0:
            self._USDToDisbursePerTick(state)
        if self.OCEAN() > 0:
            self._OCEANToDisbursePerTick(state)

        # self._s_since_buy += state.ss.time_step
