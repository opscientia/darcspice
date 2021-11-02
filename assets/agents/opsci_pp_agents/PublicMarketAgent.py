import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import random
import math

from assets.agents.opsci_pp_agents import PublicMarket, PrivateMarket
from web3engine import bfactory, bpool, datatoken, dtfactory, globaltokens
from engine.KnowledgeMarketBase import KnowledgeMarketBase
from web3tools.web3util import toBase18
from util.constants import S_PER_MONTH

@enforce_types
class PublicKnowledgeMarketAgent(KnowledgeMarketBase):
    '''
    Public knowledge market. Stores all private knowledge assets (data, algorithms, compute),
    distributes rewards to asset owners, sends fees to DAOTreasury
    Properties:
        - collects/stores knowledge assets (and OCEAN)
        - sends transaction fees to DAO Treasury & Stakers
        - sends OCEAN to Researchers for publishing knowledge assets
        - collects OCEAN (this will be a fixed ratio from the funding,
        representing the researchers publishing their research papers on the platform 
        (basically the value of their research))
    '''
    def __init__(self, name: str, USD: float, OCEAN: float,
                 transaction_fees_percentage: float,
                 fee_receiving_agents=None):
        """receiving_agents -- [agent_n_name] : method_for_%_going_to_agent_n
        The dict values are methods, not floats, so that the return value
        can change over time. E.g. percent_burn changes.
        """
        super().__init__(name, USD, OCEAN, transaction_fees_percentage, fee_receiving_agents)

    def takeStep(self, state):
        # TODO