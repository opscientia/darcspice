import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import random
import math

from assets.agents.PoolAgent import PoolAgent
from web3engine import bfactory, bpool, datatoken, dtfactory, globaltokens
from engine.AgentBase import AgentBase
from web3tools.web3util import toBase18
from util.constants import S_PER_MONTH

@enforce_types
class SimpleKnowledgeMarketAgent(AgentBase):
    
    def __init__(self, name: str, USD: float, OCEAN: float,
                 transaction_fees_percentage: float,
                 fee_receiving_agents=None):
        """receiving_agents -- [agent_n_name] : method_for_%_going_to_agent_n
        The dict values are methods, not floats, so that the return value
        can change over time. E.g. percent_burn changes.
        """
        super().__init__(name, USD, OCEAN)

    def takeStep(self, state) -> None:
        pass