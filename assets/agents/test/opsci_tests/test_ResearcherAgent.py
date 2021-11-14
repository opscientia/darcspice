'''
What do we want to test?
2 types of researchers: winner and loser 
both researchers:
- need to create a new proposal at the appropriate tick
winner:
- needs to send the grant funding to KnowledgeMarket (different fixed amount in this case)
- increase knowledge_access by 1
loser:
- needs to buy assets from KnowledgeMarket (fixed amount)
- increase knowledge_access by 1

what to check and how to check it?
Add 2 researchers, 1 who is always going to be the winner, 1 loser
initially, check if they both create the proposal at the appropriate tick (enough to be done once)
then check whether the balances they're sending to the KnowledgeMarket are correct (check the balances in their wallets)
lastly, check knowledge_access index (should be the same after each tick)
'''
from enforce_typing import enforce_types
import random

from assets.agents.opsci_agents.profit_sharing_agents.ResearcherAgent import ResearcherAgent
from assets.agents.opsci_agents.profit_sharing_agents.OpscientiaDAOAgent import OpscientiaDAOAgent
from engine import AgentBase, SimStateBase, SimStrategyBase
from engine.AgentDict import AgentDict
from util.constants import S_PER_DAY

class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        self.TICKS_BETWEEN_PROPOSALS = 2
        self.PRICE_OF_ASSETS = 1
        self.RATIO_FUNDS_TO_PUBLISH = 1
        self.FUNDING_BOUNDARY = 0

class SimState(SimStateBase.SimStateBase):
    def __init__(self, ss=None):
        super().__init__(ss)
        self.ss = SimStrategy()
        self.agents = AgentDict({})
        self.researchers: dict = {}
    def takeStep(self) -> None:
        for agent in list(self.agents.values()):
            agent.takeStep(self)

@enforce_types
def test1():
    state = SimState()

    class SimpleKnowledgeMarketAgent(AgentBase.AgentBase):
        def __init__(self, name: str, USD: float, OCEAN: float,):
            super().__init__(name, USD, OCEAN)
        def takeStep(self, state) -> None:
            pass

    state.agents["m"] = SimpleKnowledgeMarketAgent("m", 0.0, 0.0)
    state.agents["dao"] = OpscientiaDAOAgent("dao1", USD=0.0, OCEAN=10.0)
    state.agents["r0"] = ResearcherAgent(name="r0", USD=0.0, OCEAN=10.0,
                                    evaluator="dao",
                                    receiving_agents = {"m": 1.0},
                                    proposal_setup={'grant_requested': 1,
                                                    'assets_generated': 1,
                                                    'no_researchers': 1})
    state.agents["r1"] = ResearcherAgent(name="r1", USD=0.0, OCEAN=10.0,
                                    evaluator="dao",
                                    receiving_agents = {"m": 1.0},
                                    proposal_setup={'grant_requested': 2,
                                                    'assets_generated': 1,
                                                    'no_researchers': 1})
    state.researchers["r0"] = ResearcherAgent(name="r0", USD=0.0, OCEAN=10.0,
                                    evaluator="dao",
                                    receiving_agents = {"m": 1.0},
                                    proposal_setup={'grant_requested': 1,
                                                    'assets_generated': 1,
                                                    'no_researchers': 1})
    state.researchers["r1"] = ResearcherAgent(name="r1", USD=0.0, OCEAN=10.0,
                                    evaluator="dao",
                                    receiving_agents = {"m": 1.0},
                                    proposal_setup={'grant_requested': 2,
                                                    'assets_generated': 1,
                                                    'no_researchers': 1})

    assert state.agents["r0"].OCEAN() == 10.0
    assert state.agents["r1"].OCEAN() == 10.0
    assert state.agents["dao"].OCEAN() == 10.0
    assert state.agents["m"].OCEAN() == 0.0

    r0 = state.agents["r0"]
    r1 = state.agents["r1"]
    dao = state.agents["dao"]
    m = state.agents["m"]

    state.takeStep(); state.tick += 1 # create a proposal | won't be funded yet since opsci_dao is the first agent
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert not dao.proposal_evaluation
    assert r0.OCEAN() == 10.0
    assert r1.OCEAN() == 10.0
    assert dao.OCEAN() == 10.0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert dao.proposal_evaluation
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 9.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 9.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 9.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 9.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0
    
    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 8.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 8.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 8.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 8.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 7.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 7.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 7.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 7.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 6.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 6.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 6.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 6.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 5.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 5.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 5.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 5.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 4.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 4.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1
    
    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 4.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 4.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 3.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 3.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 3.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 3.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0
    
    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 2.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 2.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 2.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 2.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 1.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 1.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    state.takeStep(); state.tick += 1 # create a proposal | SHOULD NOT BE FUNDED UNTIL NEXT ROUND
    assert r0.proposal
    assert r0.new_proposal == True
    assert r1.proposal
    assert r1.new_proposal == True
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 1.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 1.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 0
    assert r1.ticks_since_proposal == 0

    state.takeStep(); state.tick += 1 # fund & publish
    assert r0.proposal
    assert r0.new_proposal == False
    assert r1.proposal
    assert r1.new_proposal == False
    assert r0.OCEAN() == 10.0 # winner receives 1 OCEAN but immediatelly spends it
    assert r1.OCEAN() == 0.0 # loser uses one 1 OCEAN to buy from Knowledge Market
    assert dao.OCEAN() == 0.0 # dao sent 1 OCEAN to r1 (winner)
    assert r0.ticks_since_proposal == 1
    assert r1.ticks_since_proposal == 1

    assert r0.total_assets_in_mrkt == 10
    assert r1.total_assets_in_mrkt == 0
    assert r0.knowledge_access == 11
    assert r1.knowledge_access == 11
    assert m.OCEAN() == 20