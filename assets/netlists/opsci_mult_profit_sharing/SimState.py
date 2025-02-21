from enforce_typing import enforce_types
from typing import Set
import random

from assets.agents import MinterAgents
from assets.agents.opsci_agents.mult_agents.MultResearcherAgent import MultResearcherAgent
from assets.agents.opsci_agents.mult_agents.MultDAOTreasuryAgent import MultDAOTreasuryAgent
from assets.agents.opsci_agents.mult_agents.MultKnowledgeMarketAgent import MultKnowledgeMarketAgent
from assets.agents.opsci_agents.SimpleStakerspeculatorAgent import SimpleStakerspeculatorAgent
from engine import AgentBase, SimStateBase
from .KPIs import KPIs
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, S_PER_DAY

@enforce_types
class SimState(SimStateBase.SimStateBase):
    '''
    SimState for the Web3 Open Science Profit Sharing Model
    '''
    def __init__(self, ss=None):
        #initialize self.tick, ss, agents, kpis
        super().__init__(ss)

        #now, fill in actual values for ss, agents, kpis
        if self.ss is None:
            from .SimStrategy import SimStrategy
            self.ss = SimStrategy()
        ss = self.ss #for convenience as we go forward
                                
        #as ecosystem improves, these parameters may change / improve
        self._marketplace_percent_toll_to_ocean = 0.002 #magic number
        self._percent_burn: float = 0.0005 #to burning, vs to OpsciMarketplace #magic number
        self._percent_dao: float = 0.05 #to dao vs to sellers

        self._speculation_valuation = 150e6 #in USD #magic number
        self._percent_increase_speculation_valuation_per_s = 0.10 / S_PER_YEAR # ""


        #Instantiate and connnect agent instances. "Wire up the circuit"
        new_agents: Set[AgentBase.AgentBase] = set()
        researcher_agents: Set[AgentBase.AgentBase] = set()
        self.researchers: dict = {}

        #################### Wiring of agents that send OCEAN ####################
        new_agents.add(MultDAOTreasuryAgent(
            name = "dao_treasury", USD=0.0, OCEAN=500000.0))

        new_agents.add(SimpleStakerspeculatorAgent(
            name = "staker", USD=0.0, OCEAN=90000.0))

        for i in range(ss.NUMBER_OF_RESEARCHERS):
            new_agents.add(MultResearcherAgent(
                name = "researcher%x" % i, evaluator = "dao_treasury",
                USD=0.0, OCEAN=10000.0,
                receiving_agents = {"market": 1.0}))
            researcher_agents.add(MultResearcherAgent(
                name = "researcher%x" % i, evaluator = "dao_treasury",
                USD=0.0, OCEAN=10000.0,
                receiving_agents = {"market": 1.0}))
        
        new_agents.add(MultKnowledgeMarketAgent(
            name = "market", USD=0.0, OCEAN=10000.0,
            transaction_fees_percentage=0.1,
            fee_receiving_agents={"staker": self.ss.FEES_TO_STAKERS, "dao_treasury": 1.0 - self.ss.FEES_TO_STAKERS}))

        for agent in new_agents:
            self.agents[agent.name] = agent

        for agent in researcher_agents:
            self.researchers[agent.name] = agent

        #track certain metrics over time, so that we don't have to load
        self.kpis = KPIs(self.ss.time_step)
                    
    def takeStep(self) -> None:
        """This happens once per tick"""
        #update agents
        #update kpis (global state values)
        super().takeStep()
        
        #update global state values: other
        self._speculation_valuation *= (1.0 + self._percent_increase_speculation_valuation_per_s * self.ss.time_step)

    #==============================================================      
    def marketplacePercentTollToOcean(self) -> float:
        return self._marketplace_percent_toll_to_ocean
    
    def percentToBurn(self) -> float:
        return self._percent_burn

    def percentToOpsciMrkt(self) -> float:
        return 1.0 - self._percent_burn
    
    def percentToOpsciDAO(self) -> float:
        return self._percent_dao

    def percentToSellers(self) -> float:
        return 1.0 - self._percent_dao
    
def funcOne():
    return 1.0


