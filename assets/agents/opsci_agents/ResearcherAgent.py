import logging
from enforce_typing import enforce_types
import random
from typing import List
import math

from assets.agents.PoolAgent import PoolAgent
from engine.AgentBase import AgentBase
from web3engine import bpool, datatoken, globaltokens
from web3tools.web3util import fromBase18, toBase18
log = logging.getLogger('agents')

@enforce_types
class ResearcherAgent(AgentBase):
    '''
    ResearcherAgent publishes proposals, creates knowledge assets and publishes them to a knowledge curator.
    Has functionality of both PublisherAgent and DataconsumerAgent
    Also, it keeps track of the following metrics:
    - number of proposals submitted
    - number of proposals funded
    - total funds received for research
    '''   
    def __init__(self, name: str, evaluator: str, USD: float, OCEAN: float,
                 receiving_agents : dict, proposal_setup : dict = None):
        super().__init__(name, USD, OCEAN)
        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent
        self._receiving_agents = receiving_agents
        self._evaluator = evaluator
        self.proposal_setup = proposal_setup

        self.proposal = None
        self.knowledge_access: float = 1.0
        self.ticks_since_proposal: int = 0
        self.proposal_accepted = False
        self.tick_of_proposal = 0

        # metrics to track
        self.no_proposals_submitted: int = 0
        self.no_proposals_funded: int = 0
        self.total_research_funds_received: float = 0.0
        self.total_assets_in_mrkt: int = 0

        self.ratio_funds_to_publish = 0.4 # arbitrary, could experiment with different values

        self._last_check_tick = 0
        self.last_tick_spent = 0 # used by KnowledgeMarket to determine who just sent funds
    
    def createProposal(self, state) -> dict:
        self.tick_of_proposal = state.tick
        if self.proposal_setup is not None:
            self.proposal = self.proposal_setup
            self.proposal['knowledge_access'] = self.knowledge_access
            return self.proposal
        else:
            return {'grant_requested': random.randint(10000, 50000), # Note: might be worth considering some distribution based on other params
                    'assets_generated': random.randint(1, 10), # Note: might be worth considering some distribution based on other params 
                    'no_researchers': 10,
                    'knowledge_access': self.knowledge_access}

    def spentAtTick(self) -> float:
        return self._spent_at_tick

    def _USDToDisbursePerTick(self, state) -> None:
        '''
        1 tick = 1 hour
        '''
        USD = self.USD()
        # in this naive model, it makes little difference whether the money from grants is spent in one tick or across many
        if self.proposal != None and self.USD() != 0.0:
            for name, computePercent in self._receiving_agents.items():
                self._transferUSD(state.getAgent(name), computePercent * USD) # NOTE: computePercent() should be used when it is a function in SimState.py
    
    def _BuyAndPublishAssets(self, state) -> None:
        '''
        This is only for interaction with KnowledgeMarket. Whenever this is called,
        it is presumed that at least a part of the funds are for buying assets in the marketplace.
        1 tick = 1 hour
        '''
        OCEAN = self.OCEAN()
        if OCEAN != 0 and self.proposal is not None:
            OCEAN_DISBURSE: float = self.proposal['grant_requested']
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent * OCEAN_DISBURSE)

        self.knowledge_access += 1 # self.proposal['assets_generated'] # subject to change, but we can say that the knowledge assets published ~ knowledge gained

    def _BuyAssets(self, state) -> None:
        '''
        This is only for interaction with KnowledgeMarket. Whenever this is called,
        it is presumed that at least a part of the funds are for buying assets in the marketplace.
        1 tick = 1 hour
        '''
        OCEAN = self.OCEAN()
        if OCEAN != 0:
            OCEAN_DISBURSE =  state.ss.PRICE_OF_ASSETS # arbitrary, if Researcher starts with 10k OCEAN, it gives them 10 rounds to buy back into the competition
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent * OCEAN_DISBURSE)

        self.knowledge_access += 1
    
    def takeStep(self, state):
        self._last_check_tick += 1

        if self.proposal is not None:
            self.ticks_since_proposal += 1

        # Proposal functionality
        if self.proposal is None:
            self.proposal = self.createProposal(state)
            self.no_proposals_submitted += 1
            self.ticks_since_proposal = 0

        # checking to see whether it is time to submit a new proposal
        if (self.ticks_since_proposal % state.ss.TICKS_BETWEEN_PROPOSALS) == 0:
            self.proposal = self.createProposal(state)
            self.no_proposals_submitted += 1
            self.ticks_since_proposal = 0

        # Checking if proposal accepted (should only be checked at the tick right after the tick when createProposal() was called)
        if state.tick - self.tick_of_proposal == 1:
            # In case the funding is misaligned with the researchers
            if not state.getAgent(self._evaluator).proposal_evaluation:
                self.tick_of_proposal = state.tick
            # if I am the winner, send the funds received to KnowledgeMarket
            elif state.getAgent(self._evaluator).proposal_evaluation['winner'] == self.name:
                self.proposal_accepted = True
                self.no_proposals_funded += 1
                self.total_assets_in_mrkt += self.proposal['assets_generated']
                self.total_research_funds_received += self.proposal['grant_requested']
                if self.OCEAN() >= self.proposal['grant_requested']:
                    self.ratio_funds_to_publish = 0.4 # KnowledgeMarketAgent will check this parameter
                    self.last_tick_spent = state.tick
                    self._BuyAndPublishAssets(state)
            elif state.getAgent(self._evaluator).proposal_evaluation['winner'] != self.name:
                self.proposal_accepted = False

        # If NOT a grant winner, buy and consume DT to gain knowledge_access point | DataconsumerAgent functionality
        if (((self._last_check_tick % state.ss.TICKS_BETWEEN_PROPOSALS) == 0) or state.tick == 10):
            if (state.getAgent(self._evaluator).proposal_evaluation['winner'] != self.name):
                # BuyAndConsumeDT and increment knowledge_access
                self._last_check_tick = state.tick
                self.ratio_funds_to_publish = 0.0 # not publishing
                self.last_tick_spent = state.tick
                self._BuyAssets(state)

        # self._spent_at_tick = self.USD() + self.OCEAN() * state.OCEANprice()
        self._spent_at_tick = self.OCEAN()

        if self.USD() > 0:
            self._USDToDisbursePerTick(state)
        
        # self._s_since_buy += state.ss.time_step
