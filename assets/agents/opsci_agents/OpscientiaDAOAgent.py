import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import math

from engine.AgentBase import AgentBase
from util.constants import S_PER_MONTH, TICKS_BETWEEN_PROPOSALS

@enforce_types
class OpscientiaDAOAgent(AgentBase):
    '''
    Sends OCEAN to be burned, evaluates proposals, disburses funds to researchers (TODO) (acts as a treasury)
    '''
    def __init__(self, name: str, USD: float, OCEAN: float,
                 receiving_agents=None):
        """receiving_agents -- [agent_n_name] : method_for_%_going_to_agent_n
        The dict values are methods, not floats, so that the return value
        can change over time. E.g. percent_burn changes.
        """
        super().__init__(name, USD, OCEAN)
        self._receiving_agents = receiving_agents

        #track amounts over time
        self._USD_per_tick: List[float] = [] #the next tick will record what's in self
        self._OCEAN_per_tick: List[float] = [] # ""

        self.proposal_evaluation: Dict = {}

        self._USD_per_grant: float = 0.0
        self._OCEAN_per_grant: float = 0.0
        
        self.proposal_funded = False
        self.tick_proposal_funded = 0

        # metrics to track (and to cross-correlate with ResearcherAgents)
        self.no_proposals_received: int = 0
        self.total_research_funds_disbursed: float = 0.0

    def evaluateProposal(self, state) -> dict:
        '''
        Function that evaluates proposals from all researcher agents.
        A proposal has 4 parameters that will be used to evaluate it.
        -------
        Params:
            grant_requested
            no_researchers
            assets_generated
        -------
        These parameters are then evaluated as (grant_requested / no_researchers) / assets_generated.
        The proposal with the smaller score is accepted. 
        '''
        r0 = state.getAgent('researcher0')
        r1 = state.getAgent('researcher1')

        if r0.proposal != None and r1.proposal != None:
            r0_score = (r0.proposal['grant_requested'] / r0.proposal['no_researchers']) / r0.proposal['assets_generated'] / r0.proposal['knowledge_access']
            r1_score = (r1.proposal['grant_requested'] / r1.proposal['no_researchers']) / r1.proposal['assets_generated'] / r1.proposal['knowledge_access']

            if r0_score < r1_score:
                return {'winner': "researcher0", 'amount': r0.proposal['grant_requested'], 'loser': "researcher1"}
            else:
                return {'winner': "researcher1", 'amount': r1.proposal['grant_requested'], 'loser': "researcher0"}
        return {}

    def proposalsReady(self, state):
        if (state.getAgent('researcher0').proposal is not None) and (state.getAgent('researcher1').proposal is not None):
            return True

    def takeStep(self, state) -> None:
        can_fund = self.proposalsReady(state)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())
                
        if (((self.tick_proposal_funded - state.tick) % TICKS_BETWEEN_PROPOSALS) == 0) and can_fund:
            self.proposal_evaluation = self.evaluateProposal(state)
            self._disburseFundsOCEAN(state)
            self.tick_proposal_funded = state.tick
            self.proposal_funded = True
            self.no_proposals_received += 1
            self.total_research_funds_disbursed += self.proposal_evaluation['amount']
        elif (state.tick == 1 or state.tick == 2) and (self.proposal_funded is False) and can_fund:
            self.proposal_evaluation = self.evaluateProposal(state)
            self._disburseFundsOCEAN(state)
            self.tick_proposal_funded = state.tick
            self.proposal_funded = True
            self.no_proposals_received += 1
            self.total_research_funds_disbursed += self.proposal_evaluation['amount']
        
        # Used for transferring funds to any other agent (not ResearcherAgent)
        # if self.USD() > 0:
        #     self._disburseUSD(state)
        # if self.OCEAN() > 0:
        #     self._disburseOCEAN(state)

    def _disburseFundsOCEAN(self, state):
        if self.proposal_evaluation != None:        
            OCEAN = min(self.OCEAN(), self.proposal_evaluation['amount'])
            agent = state.getAgent(self.proposal_evaluation['winner'])
            self._transferOCEAN(agent, OCEAN)
    
    def _disburseFundsUSD(self, state):
        if self.proposal_evaluation != None:        
            USD = min(self.USD(), self.proposal_evaluation['amount'])
            agent = state.getAgent(self.proposal_evaluation['winner'])
            self._transferUSD(agent, USD)

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1
        