import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import random
import math

from web3engine import bfactory, bpool, datatoken, dtfactory, globaltokens
from engine.AgentBase import AgentBase
from web3tools.web3util import toBase18
from util.constants import S_PER_MONTH

@enforce_types
class PublicKnowledgeMarketAgent(AgentBase):
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
        super().__init__(name, USD, OCEAN)
        self._receiving_agents = fee_receiving_agents

        #track amounts over time
        self._USD_per_tick: List[float] = [] #the next tick will record what's in self
        self._OCEAN_per_tick: List[float] = [] # ""

        self.OCEAN_last_tick = 0.0
        self.transaction_fees_percentage = transaction_fees_percentage
        self.total_fees: float = 0.0


        self.knowledge_assets_per_researcher = {}
        self.knowledge_assets = {}
        self.total_knowledge_assets = 0
        self.types = ['algo', 'data', 'compute']

    def _ToDistribute(self, state):
        received = self.OCEAN() - self.OCEAN_last_tick
        if received > 0:
            fees = 0
            OCEAN_to_self = 0
            sum_OCEAN_received = 0.0

            # iterate through all researchers
            for researcher in state.researchers.keys():
                r = state.getAgent(researcher)
                # if r.last_tick_spent == (state.tick-1) or r.last_tick_spent == state.tick or r.last_tick_spent == (state.tick - 2):

                # get the OCEAN received by this agent (add it to total for assertion later)
                received_from_r = r.last_OCEAN_spent

                # make sure the researcher is really buying from this market
                if received_from_r['market'] == 'private_market':
                    continue
                assert received_from_r['market'] == 'public_market'

                sum_OCEAN_received += received_from_r['spent']
                ratio = received_from_r['ratio']
                # print(f"RESEARCHER: {r.name} | received_from {received_from_r} | RATIO: {ratio}")

                # new publishing functionality | if the researcher is publishing assets to the marketplace
                if received_from_r['publish'] and r.research_type == 'public':
                    # add total knowledge_assets
                    self.total_knowledge_assets += r.proposal['assets_generated']
                    if r.asset_type not in self.knowledge_assets.keys():
                        self.knowledge_assets[r.asset_type] = r.proposal['assets_generated']
                    else:
                        self.knowledge_assets[r.asset_type] += r.proposal['assets_generated']

                # calculate fee for this transaction
                r_fee = received_from_r['spent'] * self.transaction_fees_percentage
                fees += r_fee # append it to total fees

                # to self
                OCEAN_to_self += (received_from_r['spent'] - r_fee) * ratio
                fees += received_from_r -r_fee - OCEAN_to_self # since this is public, on top of the fees, the price for the asset also goes to the treasury
            
            assert round(sum_OCEAN_received, 5) == round(received, 5) # sum of the OCEAN received from researchers must equal the total received
            assert round(fees, 5) == round(received * self.transaction_fees_percentage, 5) # same logic
            return fees, OCEAN_to_self
        else:
            return 0, 0

    def _disburseFeesOCEAN(self, state, fee) -> None:
        '''
        Sends transaction fees to DAO Treasury and to Stakers
        ratio of fees transferred is determined by the amount of OCEAN left in treasury vs. the amount 
        of OCEAN staked by Stakers
        '''
        self.total_fees += fee
        total = 0
        for percent in self._receiving_agents.values():
            total += fee*percent
        assert (round(total, 1) == round(fee, 1))
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent * fee)

    
    def takeStep(self, state):
        fee, keep = self._ToDistribute(state)
        
        # for debugging, delete later
        if self.OCEAN_last_tick == self.OCEAN():
            fee, disburse = 0, 0

        if fee > 0:
            self._disburseFeesOCEAN(state, fee)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())

        if fee != 0 and disburse == 0:
            assert self.OCEAN_last_tick != self.OCEAN()
        self.OCEAN_last_tick = self.OCEAN()