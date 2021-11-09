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
class MultKnowledgeMarketAgent(AgentBase):
    '''
    Works like KnowledgeMarketAgent but is adapted use the slightly more complex proposal_evaluation
    from MultDAOTreasuryAgent
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
        if received > 0 and state.tick > 0:
            fees = received * self.transaction_fees_percentage
            for researcher in state.researchers.keys():
                if state.getAgent(researcher).last_tick_spent == (state.tick or state.tick-1):
                    ratio = state.getAgent(researcher).ratio_funds_to_publish
                    OCEAN_to_self = (received - fees) * ratio
                    OCEAN_to_researchers = (received - fees) - OCEAN_to_self
                    assert(round(OCEAN_to_self + OCEAN_to_researchers + fees, 2) == round(received, 2)) # sometimes the sum is different from received by xE-12
                    return fees, OCEAN_to_self, OCEAN_to_researchers
            return 0, 0, 0
        else:
            return 0, 0, 0

    def takeStep(self, state) -> None:
        self.last_research_tick += 1
        #1. check if some agent funds to you and send the transaction fees to Treasury and Stakers
        fee, keep, disburse = self._ToDistribute(state)

        if fee > 0:
            self._disburseFeesOCEAN(state, fee)

        if disburse > 0:
            self._disburseOCEANPayout(state, disburse)

        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())

        treasury = state.getAgent(state.ss.TREASURY)

        # At the end of a research project, add knowledge assets
        if (((self.last_research_tick - state.tick) % state.ss.TICKS_BETWEEN_PROPOSALS) == 0) and treasury.proposal_evaluation:
            # iterate through all winning proposals
            for ev in treasury.proposal_evaluation.keys():
                winner = treasury.proposal_evaluation[ev]['winner']
                proposal = state.getAgent(winner).proposal
                if winner in self.knowledge_assets_per_researcher:
                    self.knowledge_assets_per_researcher[winner] += proposal['assets_generated']
                else:
                    self.knowledge_assets_per_researcher[winner] = proposal['assets_generated']
                self.total_knowledge_assets += proposal['assets_generated']
            self.last_research_tick = state.tick
        elif state.tick == 20: # arbitrary, just needs to happen after the research funds have been exhausted
            for ev in treasury.proposal_evaluation.keys():
                winner = treasury.proposal_evaluation[ev]['winner']
                proposal = state.getAgent(winner).proposal
                self.knowledge_assets_per_researcher[winner] = proposal['assets_generated']
                self.total_knowledge_assets += proposal['assets_generated']
            self.last_research_tick = state.tick

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
        
    # DATA TOKEN COMPATIBILITY WIP
    
    # def _createPoolAgent(self, state) -> PoolAgent:        
    #     assert self.OCEAN() > 0.0, "should not call if no OCEAN"
    #     wallet = self._wallet._web3wallet
    #     OCEAN = globaltokens.OCEANtoken()
        
    #     #name
    #     pool_i = len(state.agents.filterToPool())
    #     dt_name = f'DT{pool_i}'
    #     pool_agent_name = f'pool{pool_i}'
        
    #     #new DT
    #     DT = self._createDatatoken(dt_name, mint_amt=1000.0) #magic number

    #     #new pool
    #     pool_address = bfactory.BFactory().newBPool(from_wallet=wallet)
    #     pool = bpool.BPool(pool_address)

    #     # Set swap fee
    #     pool.setSwapFee(self.transaction_fees_percentage, from_wallet=wallet)

    #     #bind tokens & add initial liquidity
    #     OCEAN_bind_amt = self.OCEAN() #magic number: use all the OCEAN
    #     DT_bind_amt = 20.0 #magic number
                
    #     DT.approve(pool.address, toBase18(DT_bind_amt), from_wallet=wallet)
    #     OCEAN.approve(pool.address, toBase18(OCEAN_bind_amt),from_wallet=wallet)
        
    #     pool.bind(DT.address, toBase18(DT_bind_amt),
    #               toBase18(state.ss.pool_weight_DT), from_wallet=wallet)
    #     pool.bind(OCEAN.address, toBase18(OCEAN_bind_amt),
    #               toBase18(state.ss.pool_weight_OCEAN), from_wallet=wallet)
        
    #     pool.finalize(from_wallet=wallet)

    #     #create agent
    #     pool_agent = PoolAgent(pool_agent_name, pool)
    #     state.addAgent(pool_agent)
    #     self._wallet.resetCachedInfo()
        
    #     return pool_agent
    
    # def _doUnstakeOCEAN(self, state) -> bool:
    #     if not state.agents.filterByNonzeroStake(self):
    #         return False
    #     return self._s_since_unstake >= self._s_between_unstake

    # def _unstakeOCEANsomewhere(self, state):
    #     """Choose what pool to unstake and by how much. Then do the action."""
    #     pool_agents = state.agents.filterByNonzeroStake(self)
    #     pool_agent = random.choice(list(pool_agents.values()))
    #     BPT = self.BPT(pool_agent.pool)
    #     BPT_unstake = 0.10 * BPT #magic number
    #     self.unstakeOCEAN(BPT_unstake, pool_agent.pool)

    # def _doSellDT(self, state) -> bool:
    #     if not self._DTsWithNonzeroBalance(state):
    #         return False
    #     return self._s_since_sellDT >= self._s_between_sellDT

    # def _sellDTsomewhere(self, state, perc_sell:float=0.01):
    #     """Choose what DT to sell and by how much. Then do the action."""
        
    #     cand_DTs = self._DTsWithNonzeroBalance(state)
    #     assert cand_DTs, "only call this method if have DTs w >0 balance"
    #     DT = random.choice(cand_DTs)
        
    #     DT_balance_amt = self.DT(DT)
    #     assert DT_balance_amt > 0.0
    #     DT_sell_amt = perc_sell * DT_balance_amt #magic number
                
    #     cand_pools = self._poolsWithDT(state, DT)
    #     assert cand_pools, "there should be at least 1 pool with this DT"
    #     pool = random.choice(cand_pools)
        
    #     self._wallet.sellDT(pool, DT, DT_sell_amt)

    # def _poolsWithDT(self, state, DT:datatoken.Datatoken) -> list:
    #     """Return a list of pools that have this DT. Typically exactly 1 pool"""
    #     return [pool_agent.pool
    #             for pool_agent in state.agents.filterToPool().values()
    #             if pool_agent.datatoken.address == DT.address]

    # def _DTsWithNonzeroBalance(self, state) -> list:
    #     """Return a list of Datatokens that this agent has >0 balance of""" 
    #     pool_agents = state.agents.filterToPool().values()
    #     DTs = [pool_agent.datatoken for pool_agent in pool_agents]
    #     return [DT for DT in DTs if self.DT(DT) > 0.0]

    # def _createDatatoken(self,dt_name:str,mint_amt:float)-> datatoken.Datatoken:
    #     """Create datatoken contract and mint DTs to self."""
    #     wallet = self._wallet._web3wallet
    #     DT_address = dtfactory.DTFactory().createToken(
    #         '', dt_name, dt_name, toBase18(mint_amt), from_wallet=wallet)
    #     DT = datatoken.Datatoken(DT_address)
    #     DT.mint(wallet.address, toBase18(mint_amt), from_wallet=wallet)
    #     self._wallet.resetCachedInfo()
    #     return DT