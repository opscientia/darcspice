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
class PrivateKnowledgeMarketAgent(AgentBase):
    '''
    Private knowledge market. Stores all private knowledge assets (data, algorithms, compute),
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
            OCEAN_to_researchers = {}
            sum_OCEAN_received = 0.0

            # iterate through all researchers
            for researcher in state.researchers.keys():
                r = state.getAgent(researcher)
                # if r.last_tick_spent == (state.tick-1) or r.last_tick_spent == state.tick or r.last_tick_spent == (state.tick - 2):

                # get the OCEAN received by this agent (add it to total for assertion later)
                received_from_r = r.last_OCEAN_spent

                # make sure the researcher is really buying from this market
                if received_from_r['market'] == 'public_market':
                    continue
                assert received_from_r['market'] == 'private_market'

                sum_OCEAN_received += received_from_r['spent']
                ratio = received_from_r['ratio']
                # print(f"RESEARCHER: {r.name} | received_from {received_from_r} | RATIO: {ratio}")

                # new publishing functionality | if the researcher is publishing assets to the marketplace
                if received_from_r['publish']:
                    # add total knowledge_assets
                    self.total_knowledge_assets += 1
                    if r.asset_type not in self.knowledge_assets.keys():
                        self.knowledge_assets[r.asset_type] = 1
                    else:
                        self.knowledge_assets[r.asset_type] += 1
                    # keep track of ownership of knowledge_assets
                    if r in self.knowledge_assets_per_researcher[r.asset_type]: # check if this researcher already published sth
                        self.knowledge_assets_per_researcher[r.asset_type][r] += 1
                    else:
                        self.knowledge_assets_per_researcher[r.asset_type][r] = 1

                # calculate fee for this transaction
                r_fee = received_from_r['spent'] * self.transaction_fees_percentage
                fees += r_fee # append it to total fees

                # to self
                OCEAN_to_self += (received_from_r - r_fee) * ratio

                # add the appropriate amount to researchers
                if received_from_r['asset_buy'] not in OCEAN_to_researchers:
                    OCEAN_to_researchers[received_from_r['asset_buy']] = (received_from_r['spent'] - r_fee) - (received_from_r['spent'] - r_fee) * ratio
                else:
                    OCEAN_to_researchers[received_from_r['asset_buy']] += (received_from_r['spent'] - r_fee) - (received_from_r['spent'] - r_fee) * ratio
            
            assert round(sum_OCEAN_received, 5) == round(received, 5) # sum of the OCEAN received from researchers must equal the total received
            assert round(fees, 5) == round(received * self.transaction_fees_percentage, 5) # same logic
            return fees, OCEAN_to_self, OCEAN_to_researchers
        else:
            return 0, 0, 0

    def _disburseOCEANPayout(self, state, disburse) -> None:
        '''
        Send OCEAN payout according to the ownership of assets in the KnowledgeMarket
        Receivers: ResearcherAgents
        '''
        for t in self.knowledge_assets.keys():
            assert sum(self.knowledge_assets_per_researcher[t].values() == self.knowledge_assets[t]) # assert the total is the same as the sum of all the individuals

        # get the ratios of assets (differentiated by type) of all researchers
        ratios = {}
        for type, agents in self.knowledge_assets_per_researcher.items():
            for agent, count in agents.items():
                ratios[type][agent] = count / self.knowledge_assets[type]

        for type in self.types:
            if sum(ratios[type].values()) != 0:
                assert round(sum(ratios[type].values()), 1) == 1
                for name, ratio in ratios[type].items():
                    self._transferOCEAN(state.getAgent(name), disburse[type] * ratio)

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
        fee, keep, disburse = self._ToDistribute(state)
        
        # for debugging, delete later
        if self.OCEAN_last_tick == self.OCEAN():
            fee, disburse = 0, 0

        if fee > 0:
            self._disburseFeesOCEAN(state, fee)

        if disburse > 0:
            self._disburseOCEANPayout(state, disburse)

        if fee != 0 and disburse == 0:
            assert self.OCEAN_last_tick != self.OCEAN()
        self.OCEAN_last_tick = self.OCEAN()