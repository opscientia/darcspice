import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import math

from engine.AgentBase import AgentBase
from util.constants import S_PER_MONTH
# Note: TICKS_BETWEEN_PROPOSALS should not be in constants but rather in SimStrategy

@enforce_types
class MultTimeDAOTreasuryAgent(AgentBase):
    '''
    MultDAOTreasuryAgent but funding is disbursed on a rolling basis
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
        self.update: int = 0

        self._USD_per_grant: float = 0.0
        self._OCEAN_per_grant: float = 0.0

        # metrics to track (and to cross-correlate with ResearcherAgents)
        self.total_research_funds_disbursed: float = 0.0

    def evaluateProposal(self, state) -> None:
        '''
        Function that evaluates proposals from all researcher agents.
        A proposal has 5 parameters that will be used to evaluate it.
        -------
        Params:
            grant_requested
            no_researchers
            assets_generated
            time
            knwoledge_access
        -------
        The proposal with the smaller score is accepted. 
        '''            
        scores = {}
        # Ensure that scores and names consist of research proposals NOT currently funded
        for name in state.researchers.keys():
            # I don't want to fund proposals that are already in proposal_evaluation
            if self.proposal_evaluation:
                if name in list(self.proposal_evaluation.values())[0].values():
                    continue
            agent = state.getAgent(name)
            scores[name] = agent.proposal['grant_requested'] / \
                              agent.proposal['no_researchers'] /  \
                              agent.proposal['assets_generated'] / \
                              agent.proposal['time'] / \
                              agent.proposal['knowledge_access']

        start_idx = list(self.proposal_evaluation.keys())[-1] if self.proposal_evaluation else 0
        for i in range(start_idx, start_idx + state.ss.PROPOSALS_FUNDED_AT_A_TIME): # ensures unique indeces for the evaluation
            winner = min(scores, key=scores.get)
            self.proposal_evaluation[i] = {'winner': winner, 'amount': state.getAgent(winner).proposal['grant_requested']}
            del scores[winner]

            # immediately disburse funds to new winner
            self._disburseFundsOCEAN(state, i)
            self.total_research_funds_disbursed += self.proposal_evaluation[i]['amount']
            self.update += 1
            # check if enough OCEAN for next grant
            if self.OCEAN() < 10000: # arbitrary number
                break
            if len(self.proposal_evaluation.keys()) == state.ss.PROPOSALS_FUNDED_AT_A_TIME:
                break
        assert (len(self.proposal_evaluation.keys()) <= state.ss.PROPOSALS_FUNDED_AT_A_TIME)

    def checkProposalState(self, state):
        '''Checks the currently funded proposals to see whether it is finished or not'''
        for i, proposal in list(self.proposal_evaluation.items()):
            if state.getAgent(proposal['winner']).research_finished:
                del self.proposal_evaluation[i]
                print(self.proposal_evaluation)

    def proposalsReady(self, state):
        if all(state.getAgent(name).proposal is not None for name in state.researchers.keys()):
            self._proposals_to_evaluate = [state.getAgent(name).proposal for name in state.researchers.keys()]
            return True

    def takeStep(self, state) -> None:
        can_fund = self.proposalsReady(state) and (self.OCEAN() > 10000)
        self.update = 0 # if no evaluateProposal is called this will remain 0
        # This is an issue if there are multiple research proposals funded
        if not can_fund:
            self.proposal_evaluation = {}
        
        if (not self.proposal_evaluation) and can_fund:
            self.evaluateProposal(state)
        # should run only if a proposal_evaluation exists
        if self.proposal_evaluation:
            self.checkProposalState(state)
            if len(self.proposal_evaluation) < state.ss.PROPOSALS_FUNDED_AT_A_TIME:
                if can_fund:
                    self.evaluateProposal(state)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())
                

    def _disburseFundsOCEAN(self, state, i):
        assert self.proposal_evaluation
        OCEAN = min(self.OCEAN(), self.proposal_evaluation[i]['amount'])
        agent = state.getAgent(self.proposal_evaluation[i]['winner'])
        self._transferOCEAN(agent, OCEAN)