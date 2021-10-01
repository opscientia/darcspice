import math
from typing import List
from enforce_typing import enforce_types

from engine.AgentBase import AgentBase

from util.constants import S_PER_MONTH

@enforce_types
class SellerAgent(AgentBase):
    '''
    Seller of assets in the Opscientia Marketplace (sells data, algorithms, compute services, etc.)
    In the naive model, sellers only receive rewards at each step from the sales of their assets.

    Note: there are two ways to track the increasing number of sellers and the revenue per tick. Either
    we increase the number of sellers at each step and track the metrics from this class, or we can have 
    just one seller agent in the loop and use the number of assets in the marketplace as an indicator of 
    the number of sellers and their rewards.
    '''
    def __init__(self, name: str, USD: float, OCEAN: float):
        super().__init__(name, USD, OCEAN)

        #track amounts over time
        self._USD_per_tick: List[float] = [] #the next tick will record what's in self
        self._OCEAN_per_tick: List[float] = [] # ""
        self._n_sellers_per_tick = 0
    
    def takeStep(self) -> None:
        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())
        self._n_sellers_per_tick += 1

    def revenuePerSellerPerSecond():
        #TODO
        return

    def numSellers():
        #TODO
        return

    def revenuePerTick():
        #TODO
        return

    def monthlyUSDreceived(self, state) -> float:
        """Amount of USD received in the past month.
        Assumes that it disburses USD as soon as it gets it."""
        tick1 = self._tickOneMonthAgo(state)
        tick2 = state.tick
        return float(sum(self._USD_per_tick[tick1:tick2+1]))
    
    def monthlyOCEANreceived(self, state) -> float:
        """Amount of OCEAN received in the past month. 
        Assumes that it disburses OCEAN as soon as it gets it."""
        tick1 = self._tickOneMonthAgo(state)
        tick2 = state.tick
        return float(sum(self._OCEAN_per_tick[tick1:tick2+1]))

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1
    