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
class PrivateKnowledgeMarketAgent(KnowledgeMarketBase):
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
        super().__init__(name, USD, OCEAN, transaction_fees_percentage, fee_receiving_agents)

        self.knowledge_assets_per_researcher = {}
        self.knowledge_assets = {}

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
        ratios = {}
        for agent, no_assets in self.knowledge_assets_per_researcher.items():
            ratios[agent] = no_assets / self.total_knowledge_assets
        assert(sum(self.knowledge_assets_per_researcher.values()) == self.total_knowledge_assets)
        if sum(ratios.values()) != 0:
            assert(round(sum(ratios.values()), 1) == 1)
            for name, ratio in ratios.items():
                self._transferOCEAN(state.getAgent(name), disburse * ratio)

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
        # TODO
        pass