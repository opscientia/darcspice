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
        self.setMaxTime(10, 'days') #typical runs: 10 years, 20 years, 150 years

        #===new attributes specific to this netlist===

        #initial # sellers and assets
        self.init_n_sellers = 1
        self.init_n_assets = 1

        # (taken from constants.py)
        self.TOTAL_MINTS = 1000 # better number to be determined
        self.TOTAL_OCEAN_SUPPLY = 1.41e9 
        self.INIT_OCEAN_SUPPLY = 0.49 * self.TOTAL_OCEAN_SUPPLY
        self.UNMINTED_OCEAN_SUPPLY = self.TOTAL_OCEAN_SUPPLY - self.INIT_OCEAN_SUPPLY

        self.OPF_TREASURY_USD = 2e6 #(not the true number)
        self.OPF_TREASURY_OCEAN = 200e6 #(not the true number)
        self.OPF_TREASURY_OCEAN_FOR_OCEAN_DAO = 100e6 #(not the true number)
        self.OPF_TREASURY_OCEAN_FOR_OPF_MGMT = self.OPF_TREASURY_OCEAN - self.OPF_TREASURY_OCEAN_FOR_OCEAN_DAO

        self.BDB_TREASURY_USD = 2e6 #(not the true number)
        self.BDB_TREASURY_OCEAN = 20e6  #(not the true number)

        self.pool_weight_DT    = 3.0
        self.pool_weight_OCEAN = 7.0
        assert (self.pool_weight_DT + self.pool_weight_OCEAN) == 10.0