import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
import math

from engine.AgentBase import AgentBase
from util.constants import S_PER_YEAR
    

@enforce_types
class OpsciMarketplaceAgent(AgentBase):
    '''
    Intermediary between ResearcherAgent and SellerAgent.
    Also tracks the number and revenue of SellerAgents (by tracking 
    the number and revenue per asset, which is the same as for sellers).
    '''
    def __init__(self,
                 name: str, USD: float, OCEAN: float,
                #  toll_agent_name: str,
                 n_assets: float,
                 revenue_per_asset_per_s: float,
                 time_step: int,
                 receiving_agents : dict
                 ):
        super().__init__(name, USD, OCEAN)
        # self._toll_agent_name: str = toll_agent_name
        self._receiving_agents = receiving_agents


        #set initial values. These grow over time.
        self._n_assets: float = n_assets
        self._revenue_per_asset_per_s: float = revenue_per_asset_per_s
        self._time_step: int = time_step

    def numAssets(self) -> float:
        return self._n_assets
        
    # Essentially the same as revenue per Seller per second
    def revenuePerAssetPerSecond(self) -> float:
        return self._revenue_per_asset_per_s
        
    def takeStep(self, state):
        
        self._n_assets += 1.0 
        # self._revenue_per_asset_per_s *= (1.0 + mkts_growth_rate_per_tick)

        #compute sales -> toll -> send funds accordingly
        sales = self._salesPerTick()
        # toll = sales * state.marketplacePercentTollToOcean() # TODO: assetPercentTollToDAO()
        # toll_agent = state.getAgent(self._toll_agent_name)
        # toll_agent.receiveUSD(toll)

        if self.USD() > 0:
            self._disburseUSD(state)
        if self.OCEAN() > 0:
            self._disburseOCEAN(state)

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

    def _salesPerTick(self) -> float:
        return self._n_assets * self._revenue_per_asset_per_s \
            * self._time_step

    # def _growthRatePerTick(self, g_per_year: float) -> float:
    #     """
    #     @arguments 
    #       g_per_year -- growth rate per year, e.g. 0.05 for 5% annual rate
    #     """
    #     ticks_per_year = S_PER_YEAR / float(self._time_step)
    #     g_per_tick = math.pow(g_per_year + 1, 1.0/ticks_per_year) - 1.0
    #     return g_per_tick

        
        
