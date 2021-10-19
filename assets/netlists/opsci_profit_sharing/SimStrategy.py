import math
from enforce_typing import enforce_types

from engine import SimStrategyBase
from util.constants import S_PER_HOUR

@enforce_types
class SimStrategy(SimStrategyBase.SimStrategyBase):
    def __init__(self):
        #===initialize self.time_step, max_ticks====
        super().__init__()

        #===set base-class values we want for this netlist====
        self.setTimeStep(S_PER_HOUR)
        self.setMaxTime(10, 'years') #typical runs: 10 years, 20 years, 150 years

        #===new attributes specific to this netlist===
        self.TICKS_BETWEEN_PROPOSALS = 6480
        self.PRICE_OF_ASSETS = 1000

        # DT parameters
        self.DT_init = 100.0

        # DATA TOKEN COMPATIBILITY WIP
        # # pool
        # self.DT_stake = 20.0
        # self.pool_weight_DT    = 3.0
        # self.pool_weight_OCEAN = 7.0
        # assert (self.pool_weight_DT + self.pool_weight_OCEAN) == 10.0