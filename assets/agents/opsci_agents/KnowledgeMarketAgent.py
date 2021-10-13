import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List
import math

from engine.AgentBase import AgentBase
from util.constants import S_PER_MONTH, TICKS_BETWEEN_PROPOSALS

@enforce_types
class KnowledgeMarketAgent(AgentBase):
    '''
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
                 s_between_grants: int, transaction_fees_percentage: float,
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

        self.knowledge_assets = {}

    def _FeesToDistribute(self):
        received = self.OCEAN() - self.OCEAN_last_tick
        if received > 0:
            fees = received * self.transaction_fees_percentage
            return fees
        else:
            return 0

    def takeStep(self, state) -> None:
        #1. check if some agent funds to you and send the transaction fees to Treasury and Stakers
        fee = self._FeesToDistribute()

        if fee > 0:
            self._disburseFeesOCEAN(state, fee)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())

        # At the end of a research project, add knowledge assets
        winner = state.getAgent('dao_treasury').proposal_evaluation['winner']
        proposal = state.getAgent(winner).proposal
        if (((self.last_research_tick - state.tick) % TICKS_BETWEEN_PROPOSALS) == 0):
            self.knowledge_assets[winner] += proposal['assets_generated']
            self.last_research_tick = state.tick
        elif state.tick == 20: # arbitrary, just needs to happen after the research funds have been exhausted
            self.knowledge_assets[winner] += proposal['assets_generated']
            self.last_research_tick = state.tick

        
        if self.USD() > 0:
            self._disburseUSD(state)
        if self.OCEAN() > 0:
            self._disburseOCEAN(state)

        self.OCEAN_last_tick = self.OCEAN()

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

    def _disburseFeesOCEAN(self, state, fee) -> None:
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * fee)

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1
        