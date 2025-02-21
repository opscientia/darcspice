import logging
from enforce_typing import enforce_types
import random
from typing import List
from engine.AgentBase import AgentBase

log = logging.getLogger('agents')

@enforce_types
class VersatileResearcherAgent(AgentBase):
    '''
    Works like MultTimeResearcherAgent but is adapted to the public/private research open science model
    ResearcherAgent publishes proposals, creates knowledge assets and publishes them to a knowledge curator.
    Also, it keeps track of the following metrics:
    - number of proposals submitted
    - number of proposals funded
    - total funds received for research
    '''   
    def __init__(self, name: str, 
                       USD: float, OCEAN: float,
                       receiving_agents : dict,
                       research_type: str = None,
                       asset_type: str = None,
                       evaluator: str = None,
                       proposal_setup : dict = None):
        '''
        Properties
        -----------
        research_type: str -> 'public' or 'private'
        asset_type: str -> 'data', 'algo', 'compute' ('compute' only available for 'private')
        '''
        super().__init__(name, USD, OCEAN)
        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent

        self.research_type = research_type
        self.asset_type = asset_type
        
        if self.research_type == None:
            self.research_type = random.choice(['public', 'private'])
        
        if self.asset_type == None:
            if self.research_type == 'public':
                self.asset_type = random.choice(['data', 'algo'])
            elif self.research_type == 'private':
                self.asset_type = random.choice(['data', 'algo', 'compute'])

        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent
        self._receiving_agents = receiving_agents
        self._evaluator = evaluator
        self.proposal_setup = proposal_setup
        self.integrations: list = []
        self.novelties: list = []

        self.proposal: dict = {}
        self.new_proposal = False # not sure how to utilize this yet
        self.knowledge_access: float = 1.0
        self.ticks_since_proposal: int = 0
        self.proposal_accepted = False
        self.research_finished = False

        self.private_bought_last_tick = False

        # metrics to track
        self.my_OCEAN: float = 0.0
        self.no_proposals_submitted: int = 0
        self.no_proposals_funded: int = 0
        self.total_research_funds_received: float = 0.0
        self.total_assets_in_mrkt: int = 0

        self.ratio_funds_to_publish: float = 0.0

        self.last_tick_spent = 0 # used by KnowledgeMarket to determine who just sent funds
        self.total_OCEAN_spent_this_tick: float = 0.0
        self.last_OCEAN_spent: dict = {}
        self.OCEAN_last_action: float = 0.0
    
    #### FUNCTIONS of MultTimeResearcherAgent ####
    def createProposal(self, state) -> dict:
        self.new_proposal = True
        self.research_finished = False
        if self.proposal_setup is not None:
            self.proposal = self.proposal_setup
            self.proposal['knowledge_access'] = self.knowledge_access
            return self.proposal
        else:
            return {'grant_requested': random.randint(10000, 50000), # Note: might be worth considering some distribution based on other params
                    'assets_generated': random.randint(1, 10), # Note: might be worth considering some distribution based on other params 
                    'no_researchers': 10,
                    'time': random.randint(5000, 15000), # research length: random number of ticks
                    'knowledge_access': self.knowledge_access,
                    'integration': self._getIntegration(),
                    'novelty': self._getNovelty(),
                    'impact': self._getImpact()}

    def spentAtTick(self) -> float:
        return self._spent_at_tick

    def _USDToDisbursePerTick(self, state) -> None:
        '''
        1 tick = 1 hour
        '''
        USD = self.USD()
        # in this naive model, it makes little difference whether the money from grants is spent in one tick or across many
        if (self.proposal != {}) and (self.USD() != 0.0):
            for name, computePercent in self._receiving_agents.items():
                self._transferUSD(state.getAgent(name), computePercent * USD) # NOTE: computePercent() should be used when it is a function in SimState.py
    
    def _BuyAndPublishAssets(self, state) -> None:
        '''
        This is only for interaction with KnowledgeMarket. Whenever this is called,
        it is presumed that at least a part of the funds are for buying assets in the marketplace.
        1 tick = 1 hour
        '''
        # new functionality for VersatileAgent
        _, asset_to_buy = self._getMarketAndAssets()
        OCEAN = self.OCEAN()
        self.last_tick_spent = state.tick
        self.ratio_funds_to_publish = state.ss.RATIO_FUNDS_TO_PUBLISH # KnowledgeMarketAgent will check this parameter
        if (OCEAN != 0) and (self.proposal != {}):
            OCEAN_DISBURSE: float = self.proposal['grant_requested']
            self.total_OCEAN_spent_this_tick += OCEAN_DISBURSE
            self.last_OCEAN_spent = {'tick': state.tick, 'spent': self.total_OCEAN_spent_this_tick, 'market': 'public_market', 'asset_buy': asset_to_buy, 'publish': True, 'ratio': self.ratio_funds_to_publish}
            self._transferOCEAN(state.getAgent('public_market'), OCEAN_DISBURSE)
            self.knowledge_access += 1 # self.proposal['assets_generated'] # subject to change, but we can say that the knowledge assets published ~ knowledge gained

    def _BuyAssets(self, state) -> None:
        '''
        This is only for interaction with KnowledgeMarket. Whenever this is called,
        it is presumed that at least a part of the funds are for buying assets in the marketplace.
        1 tick = 1 hour
        '''
        # new functionality for VersatileAgent
        _, asset_to_buy = self._getMarketAndAssets()

        OCEAN = self.OCEAN()
        self.last_tick_spent = state.tick
        self.ratio_funds_to_publish = 0.0 # not publishing
        if (OCEAN != 0) and (OCEAN >= state.ss.PRICE_OF_ASSETS) and (self.proposal != {}):
            OCEAN_DISBURSE =  state.ss.PRICE_OF_ASSETS # arbitrary, if Researcher starts with 10k OCEAN, it gives them 10 rounds to buy back into the competition
            self.total_OCEAN_spent_this_tick += OCEAN_DISBURSE
            self.last_OCEAN_spent = {'tick': state.tick, 'spent': self.total_OCEAN_spent_this_tick, 'market': 'public_market', 'asset_buy': asset_to_buy, 'publish': False, 'ratio': self.ratio_funds_to_publish}
            self.knowledge_access += 1
            self.proposal['knowledge_access'] = self.knowledge_access
            self._transferOCEAN(state.getAgent('public_market'), OCEAN_DISBURSE)

    def _checkIfFunded(self, state) -> None:
        prop_eval = state.getAgent(self._evaluator).proposal_evaluation
        full_proposal: bool = len(prop_eval) == state.ss.PROPOSALS_FUNDED_AT_A_TIME
        # Checking if proposal accepted (should only be checked if the DAOTreasury evaluated the proposals and I am not a winner:
        if (prop_eval != {}) and (not self.proposal_accepted) and full_proposal:
            self.new_proposal = False
            prop_evaluation = prop_eval
            # if I am the winner, send the funds received to KnowledgeMarket
            if any((prop_evaluation[i]['winner'] == self.name) for i in prop_evaluation.keys()):
                self.proposal_accepted = True
                self.ticks_since_proposal = 0 # reset ticks_since_proposal to track the time of research
                self.no_proposals_funded += 1
                self.total_assets_in_mrkt += self.proposal['assets_generated']
                self.total_research_funds_received += self.proposal['grant_requested']
                if self.OCEAN() >= self.proposal['grant_requested']:
                    self._BuyAndPublishAssets(state)
            else:
                assert(all((prop_evaluation[i]['winner'] != self.name)for i in prop_eval.keys()))
                self.proposal_accepted = False # this is kind of useless
                self.proposal = self.createProposal(state) # just create new proposal to make sure we have the random element
                if state.getAgent(self._evaluator).update > 0:
                    for _ in range(state.getAgent(self._evaluator).update):
                        self._BuyAssets(state)

    def _getIntegration(self) -> float:
        if len(self.integrations) == 0:
            integration = random.random()
        elif self.integrations[-1] < 0.5:
            integration = random.uniform(0.0, 0.5)
        elif self.integrations[-1] >= 0.5:
            integration = random.uniform(0.5, 1.0)
        self.integrations.append(integration)
        return integration

    def _getNovelty(self) -> float:
        if len(self.novelties) == 0:
            novelty = random.random()
        elif self.novelties[-1] < 0.5:
            novelty = random.uniform(0.0, 0.5)
        elif self.novelties[-1] >= 0.5:
            novelty = random.uniform(0.5, 1.0)
        self.novelties.append(novelty)
        return novelty

    def _getImpact(self) -> float:
        if self.novelties[-1] < self.integrations[-1]:
            return 10 * self.integrations[-1]
        else:
            return 10 * self.novelties[-1]
    
    def multTimeTakeStep(self, state):
        self.total_OCEAN_spent_this_tick = 0.0
        # takeStep for MultTimeResearcherAgent (and now public VersatileResearcherAgent)
        self._checkIfFunded(state)

        # Proposal functionality
        if self.proposal == {}:
            self.proposal = self.createProposal(state)
            self.no_proposals_submitted += 1
            self.ticks_since_proposal = 0

        if self.proposal != {}:
            self.ticks_since_proposal += 1
            # tracking the research progress for winning researchers
            if self.proposal_accepted:
                if self.ticks_since_proposal - self.proposal['time'] == 0:
                    self.research_finished = True
                    self.proposal = {}
                    self.proposal_accepted = False

        self.my_OCEAN = self.OCEAN()

        self._spent_at_tick = self.OCEAN()

        # if state.ss.RANDOM_BUYING:
        #     if not self.proposal_accepted and random.random() >= 0.6: # arbitrary
        #         self._BuyAssets(state)

        if self.USD() > 0:
            self._USDToDisbursePerTick(state)

    #### FUNCTIONS OF PrivateResearcherAgents ####
    def _haveROI(self) -> bool:
        if self.OCEAN() > self.OCEAN_last_action:
            return True
        else:
            return False

    def _privatePublishAssets(self, state) -> None:
        '''
        Used by private researchers to publish assets to the marketplace
        '''
        OCEAN = self.OCEAN()
        self.last_tick_spent = state.tick
        self.ratio_funds_to_publish = 1.0 # KnowledgeMarketAgent will check this parameter
        if OCEAN >= state.ss.PRIVATE_PUBLISH_COST[self.asset_type]:
            assets_generated = random.randint(1, 10)
            self.total_assets_in_mrkt += assets_generated
            OCEAN_DISBURSE: float = state.ss.PRIVATE_PUBLISH_COST[self.asset_type]
            self.last_OCEAN_spent = {'tick': state.tick, 'spent': OCEAN_DISBURSE, 'market': 'private_market', 'asset_buy': None, 'publish': True, 'ratio': self.ratio_funds_to_publish, 'assets_generated': assets_generated}
            self._transferOCEAN(state.getAgent('private_market'), OCEAN_DISBURSE)

    def _privateBuyAssets(self, state) -> None:
        '''
        Used by private data and algo providers
        1. choose private or public market
        2. for algo provider -> choose 'data' or 'compute'
        3. for data provider -> buy 'algo'
        '''
        if self.OCEAN() > 0:
            market, asset_to_buy = self._getMarketAndAssets()

            if self.OCEAN() > state.ss.ASSET_COSTS[market][asset_to_buy]:
                if self.asset_type == 'algo':
                    self.last_OCEAN_spent = {'tick': state.tick, 'spent': state.ss.ASSET_COSTS[market][asset_to_buy], 'market': market, 'asset_buy': asset_to_buy, 'publish': False, 'ratio': 0}
                    self._transferOCEAN(state.getAgent(market), state.ss.ASSET_COSTS[market][asset_to_buy])
                elif self.asset_type == 'data':
                    asset_to_buy = 'algo'
                    self.last_OCEAN_spent = {'tick': state.tick, 'spent': state.ss.ASSET_COSTS[market][asset_to_buy], 'market': market, 'asset_buy': asset_to_buy, 'publish': False, 'ratio': 0}
                    self._transferOCEAN(state.getAgent(market), state.ss.ASSET_COSTS[market][asset_to_buy])

    # HELPER FUNCTIONS
    
    def _getMarketAndAssets(self):
        market = random.choice(['private_market', 'public_market'])
        asset_to_buy = random.choice(['data', 'compute'])

        return market, asset_to_buy

    def takeStep(self, state):
        self.last_OCEAN_spent = {}

        if self.research_type == 'public':
            self.multTimeTakeStep(state)
        else:
            self.my_OCEAN = self.OCEAN()
            assert self.research_type == 'private'

            if state.getAgent(self._evaluator).update > 0:
                if not self.private_bought_last_tick:
                    self.private_bought_last_tick = True
                    self._privateBuyAssets(state) # buys assets for research | does nothing if agent is compute provider
                elif self._haveROI():
                    self._privatePublishAssets(state) # publishes results
                    self.private_bought_last_tick = False
                    self.OCEAN_last_action = self.OCEAN()