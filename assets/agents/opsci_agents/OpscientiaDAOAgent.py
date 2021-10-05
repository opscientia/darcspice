import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List
import math

from engine.AgentBase import AgentBase
from util.constants import S_PER_MONTH

@enforce_types
class OpscientiaDAOAgent(AgentBase):
    '''
    Sends OCEAN to be burned, evaluates proposals, disburses funds to researchers (TODO) (acts as a treasury)
    '''
    def __init__(self, name: str, USD: float, OCEAN: float,
                 receiving_agents : dict, s_between_grants: int):
        """receiving_agents -- [agent_n_name] : method_for_%_going_to_agent_n
        The dict values are methods, not floats, so that the return value
        can change over time. E.g. percent_burn changes.
        """
        super().__init__(name, USD, OCEAN)
        self._receiving_agents = receiving_agents

        #track amounts over time
        self._USD_per_tick: List[float] = [] #the next tick will record what's in self
        self._OCEAN_per_tick: List[float] = [] # ""

        self.proposal_evaluation = None

        self._s_between_grants: int = s_between_grants
        self._USD_per_grant: float = 0.0
        self._OCEAN_per_grant: float = 0.0
        
        self._tick_last_disburse = None

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
            r0_score = (r0.proposal['grant_requested'] / r0.proposal['no_researchers']) / r0.proposal['assets_generated']
            r1_score = (r1.proposal['grant_requested'] / r1.proposal['no_researchers']) / r1.proposal['assets_generated']

            if r0_score < r1_score:
                return {'winner': 'researcher0', 'amount': r0['grant_requested']}
            else:
                return {'winner': 'researcher1', 'amount': r1['grant_requested']}


    def takeStep(self, state) -> None:

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())
        
        do_disburse = False
        if self._tick_last_disburse is None:
            do_disburse = True
        else:
            n_ticks_since = state.tick - self._tick_last_disburse
            n_s_since = n_ticks_since * state.ss.time_step
            n_s_thr = self._s_between_grants            
            do_disburse = (n_s_since >= n_s_thr)
        
        if do_disburse:
            self.proposal_evaluation = self.evaluateProposal(state)
            self._disburseFunds()
            self._tick_last_disburse = state.tick
        
        #disburse it all, as soon as agent has it
        if self.USD() > 0:
            self._disburseUSD(state)
        if self.OCEAN() > 0:
            self._disburseOCEAN(state)

    def _disburseFunds(self):
        if self.proposal_evaluation != None:        
            OCEAN = min(self.OCEAN(), self.proposal_evaluation['amount'])
            self._transferUSD(self.proposal_evaluation['winner'], OCEAN)

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

    # def monthlyUSDreceived(self, state) -> float:
    #     """Amount of USD received in the past month. 
    #     Assumes that it disburses USD as soon as it gets it."""
    #     tick1 = self._tickOneMonthAgo(state)
    #     tick2 = state.tick
    #     return float(sum(self._USD_per_tick[tick1:tick2+1]))
    
    # def monthlyOCEANreceived(self, state) -> float:
    #     """Amount of OCEAN received in the past month. 
    #     Assumes that it disburses OCEAN as soon as it gets it."""
    #     tick1 = self._tickOneMonthAgo(state)
    #     tick2 = state.tick
    #     return float(sum(self._OCEAN_per_tick[tick1:tick2+1]))

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1
        