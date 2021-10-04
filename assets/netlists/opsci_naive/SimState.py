from enforce_typing import enforce_types
from typing import Set

from assets.agents import MinterAgents
from assets.agents.opsci_agents.ResearcherAgent import ResearcherAgent
from assets.agents.opsci_agents.OpscientiaDAOAgent import OpscientiaDAOAgent
from assets.agents.opsci_agents.SellerAgent import SellerAgent
from assets.agents.opsci_agents.OpsciMarketplaceAgent import OpsciMarketplaceAgent
from assets.agents.opsci_agents.TokenBurnerAgent import TokenBurnerAgent
from engine import AgentBase, SimStateBase
from .KPIs import KPIs
from util import valuation
from util.constants import S_PER_YEAR, S_PER_MONTH, S_PER_DAY

@enforce_types
class SimState(SimStateBase.SimStateBase):
    
    def __init__(self, ss=None):
        #initialize self.tick, ss, agents, kpis
        super().__init__(ss)

        #now, fill in actual values for ss, agents, kpis
        if self.ss is None:
            from .SimStrategy import SimStrategy
            self.ss = SimStrategy()
        ss = self.ss #for convenience as we go forward
                        
        #used to manage names
        self._next_free_marketplace_number = 0

        #used to add agents
        self._marketplace_tick_previous_add = 0
        
        #as ecosystem improves, these parameters may change / improve
        self._marketplace_percent_toll_to_ocean = 0.002 #magic number
        self._percent_burn: float = 0.05 #to burning, vs to OpsciMarketplace #magic number
        self._percent_dao: float = 0.05 #to dao vs to sellers

        self._total_OCEAN_minted: float = 0.0
        self._total_OCEAN_burned: float = 0.0
        self._total_OCEAN_burned_USD: float = 0.0

        self._speculation_valuation = 150e6 #in USD #magic number
        self._percent_increase_speculation_valuation_per_s = 0.10 / S_PER_YEAR # ""


        #Instantiate and connnect agent instances. "Wire up the circuit"
        new_agents: Set[AgentBase.AgentBase] = set()

        #################### Wiring of agents that send OCEAN ####################
        
        # 1. MinterAgent sends funds to ResearcherAgent
        new_agents.add(MinterAgents.OCEANLinearMinterAgent(
            name = "minter",
            receiving_agent_name = "opsci_dao",
            total_OCEAN_to_mint = ss.UNMINTED_OCEAN_SUPPLY,
            s_between_mints = S_PER_DAY,
            n_mints = ss.TOTAL_MINTS))

        # 2. ResearcherAgent sends funds to OpsciMarketplaceAgent and to OCEANBurnerAgent
        new_agents.add(ResearcherAgent(
            name = "researcher0", USD=0.0, OCEAN=0.0,
            receiving_agents = {"opsci_market" : self.percentToOpsciMrkt,
                                "ocean_burner" : self.percentToBurn}))

        new_agents.add(ResearcherAgent(
            name = "researcher1", USD=0.0, OCEAN=0.0,
            receiving_agents = {"opsci_market" : self.percentToOpsciMrkt,
                                "ocean_burner" : self.percentToBurn}))

        # 3. OpsciMarketplaceAgent sends funds to OpscientiaDAOAgent and to all instances of SellerAgent
        new_agents.add(OpsciMarketplaceAgent(
            name = "opsci_market", USD=0.0, OCEAN=0.0,
            receiving_agents = {"opsci_dao" : self.percentToOpsciDAO,
                                "sellers" : self.percentToSellers},
            n_assets = float(ss.init_n_assets),
            revenue_per_asset_per_s = 20e3 / S_PER_MONTH, #magic number
            time_step = self.ss.time_step))

        # 4. OpscientiaDAOAgent sends percentage of funds to OCEANBurnerAgent
        new_agents.add(OpscientiaDAOAgent(
            name = "opsci_dao", USD=0.0, OCEAN=ss.OPF_TREASURY_OCEAN,
            receiving_agents = {"ocean_burner": self.percentToBurn}))

        # 5. OCEANBurnerAgent burns all funds in wallet
        new_agents.add(TokenBurnerAgent(
            name = "ocean_burner", USD=0.0, OCEAN=0.0))
        
        new_agents.add(SellerAgent(
            name = "sellers", USD=0.0, OCEAN=0.0,
            n_sellers = float(ss.init_n_sellers),
            revenue_per_seller_per_s= 20e3 / S_PER_MONTH, #magic number
            time_step= ss.time_step
        ))

        for agent in new_agents:
            self.agents[agent.name] = agent

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

    #==============================================================
    def OCEANprice(self) -> float:
        """Estimated price of $OCEAN token, in USD"""
        price = valuation.OCEANprice(self.overallValuation(),
                                     self.OCEANsupply())
        assert price > 0.0
        return price
    
    #==============================================================
    def overallValuation(self) -> float: #in USD
        v = self.fundamentalsValuation() + \
            self.speculationValuation()
        assert v > 0.0
        return v
    
    def fundamentalsValuation(self) -> float: #in USD
        return self.kpis.valuationPS(30.0) #based on P/S=30
    
    def speculationValuation(self) -> float: #in USD
        return self._speculation_valuation
        
    #==============================================================
    def OCEANsupply(self) -> float:
        """Current OCEAN token supply"""
        return self.initialOCEAN() \
            + self.totalOCEANminted() \
            - self.totalOCEANburned()
        
    def initialOCEAN(self) -> float:
        return self.ss.INIT_OCEAN_SUPPLY
        
    def totalOCEANminted(self) -> float:
        return self._total_OCEAN_minted
        
    def totalOCEANburned(self) -> float:
        return self._total_OCEAN_burned
        
    def totalOCEANburnedUSD(self) -> float:
        return self._total_OCEAN_burned_USD
    
    
def funcOne():
    return 1.0


