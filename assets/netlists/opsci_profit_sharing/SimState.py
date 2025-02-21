from enforce_typing import enforce_types
from typing import Set
import random
from assets import agents

from assets.agents import MinterAgents
from assets.agents.opsci_agents.profit_sharing_agents.ResearcherAgent import ResearcherAgent
from assets.agents.opsci_agents.profit_sharing_agents.OpscientiaDAOAgent import OpscientiaDAOAgent
from assets.agents.opsci_agents.profit_sharing_agents.KnowledgeMarketAgent import KnowledgeMarketAgent
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

        #Instantiate and connnect agent instances. "Wire up the circuit"
        new_agents = []
        researcher_agents = []
        self.researchers: dict = {}

        #################### Wiring of agents that send OCEAN ####################
        new_agents.append(OpscientiaDAOAgent(
            name = "dao_treasury", USD=0.0, OCEAN=500000.0))

        new_agents.append(SimpleStakerspeculatorAgent(
            name = "staker", USD=0.0, OCEAN=90000.0))

        for i in range(ss.NUMBER_OF_RESEARCHERS):
            new_agents.append(ResearcherAgent(
                name = "researcher%x" % i, evaluator = "dao_treasury",
                USD=0.0, OCEAN=10000.0,
                receiving_agents = {"market": 1.0}))
            researcher_agents.append(ResearcherAgent(
                name = "researcher%x" % i, evaluator = "dao_treasury",
                USD=0.0, OCEAN=10000.0,
                receiving_agents = {"market": 1.0}))
        
        new_agents.append(KnowledgeMarketAgent(
            name = "market", USD=0.0, OCEAN=0.0,
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