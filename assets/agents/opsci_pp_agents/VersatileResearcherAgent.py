import logging
from enforce_typing import enforce_types
import random
from typing import List

from engine.ResearcherBase import ResearcherBase
log = logging.getLogger('agents')

@enforce_types
class VersatileResearcherAgent(ResearcherBase):
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
        super().__init__(name, USD, OCEAN, receiving_agents, evaluator, proposal_setup)
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

        # metrics to track
        self.my_OCEAN: float = 0.0
        self.no_proposals_submitted: int = 0
        self.no_proposals_funded: int = 0
        self.total_research_funds_received: float = 0.0
        self.total_assets_in_mrkt: int = 0

        self.ratio_funds_to_publish: float = 0.0

        self.last_tick_spent = 0 # used by KnowledgeMarket to determine who just sent funds
        self.last_OCEAN_spent = 0.0

    def takeStep(self, state):

        if self.research_type == 'public':
            self.multTimeTakeStep(state)
        else:
            assert self.research_type == 'private'

            if random.random() < 0.1:
                self._privateBuyAssets(state) # buys assets for research | does nothing if agent is compute provider
                self._privatePublishAssets(state) # publishes results