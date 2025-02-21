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
class MultTimeKnowledgeMarketAgent(AgentBase):
    '''
    Works like MultKnowledgeMarketAgent but is adapted for the rolling basis funding
    Properties:
        - collects/stores knowledge assets (and OCEAN)
        - sends transaction fees to DAO Treasury & Stakers
        - sends OCEAN to Researchers for publishing knowledge assets
        - collects OCEAN (this will be a fixed ratio from the funding, 
        representing the researchers publishing their research papers on the platform 
        (basically the value of their research))
    
    Also has properties of a PoolAgent
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

        self.last_research_tick = 0

        self.knowledge_assets_per_researcher: Dict[str, int] = {}
        self.total_knowledge_assets: int = 0
        self.total_fees: float = 0.0

    def _ToDistribute(self, state):
        received = self.OCEAN() - self.OCEAN_last_tick
        if received > 0:
            fees = 0
            OCEAN_to_self = 0
            OCEAN_to_researchers = 0
            sum_OCEAN_received = 0.0

            # iterate through all researchers
            for researcher in state.researchers.keys():
                r = state.getAgent(researcher)
                # if r.last_tick_spent == (state.tick-1) or r.last_tick_spent == state.tick or r.last_tick_spent == (state.tick - 2):

                    # get the OCEAN received by this agent (add it to total for assertion later)
                received_from_r = r.last_OCEAN_spent
                sum_OCEAN_received += received_from_r
                ratio = r.ratio_funds_to_publish
                # print(f"RESEARCHER: {r.name} | received_from {received_from_r} | RATIO: {ratio}")

                    # calculate fee for this transaction
                r_fee = received_from_r * self.transaction_fees_percentage
                fees += r_fee # append it to total fees

                    # add the appropriate amount to self and researchers
                OCEAN_to_self += (received_from_r - r_fee) * ratio
                OCEAN_to_researchers += (received_from_r - r_fee) - (received_from_r - r_fee) * ratio
            
            assert round(sum_OCEAN_received, 5) == round(received, 5) # sum of the OCEAN received from researchers must equal the total received
            assert round(fees, 5) == round(received * self.transaction_fees_percentage, 5) # same logic
            return fees, OCEAN_to_self, OCEAN_to_researchers
        else:
            return 0, 0, 0

    def takeStep(self, state) -> None:
        self.last_research_tick += 1
        #1. check if some agent funds to you and send the transaction fees to Treasury and Stakers
        fee, keep, disburse = self._ToDistribute(state)
        
        # for debugging, delete later
        if self.OCEAN_last_tick == self.OCEAN():
            fee, disburse = 0, 0


        if fee > 0:
            self._disburseFeesOCEAN(state, fee)

        if disburse > 0:
            self._disburseOCEANPayout(state, disburse)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())

        treasury = state.getAgent(state.ss.TREASURY)

        # At the end of a research project, add knowledge assets
        if treasury.proposal_evaluation_update and treasury.update > 0:
            # iterate through all winning proposals
            for ev in treasury.proposal_evaluation_update.keys():
                winner = treasury.proposal_evaluation_update[ev]['winner']
                proposal = state.getAgent(winner).proposal
                if winner in self.knowledge_assets_per_researcher:
                    self.knowledge_assets_per_researcher[winner] += proposal['assets_generated']
                else:
                    self.knowledge_assets_per_researcher[winner] = proposal['assets_generated']
                self.total_knowledge_assets += proposal['assets_generated']
            self.last_research_tick = state.tick

        if fee != 0 and disburse == 0:
            assert self.OCEAN_last_tick != self.OCEAN()
        self.OCEAN_last_tick = self.OCEAN()

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

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

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1