"""
Netlist to simulate the Open Science Ecosystem, with no EVM
"""

#These puts all key interfaces in one module
#
#Users just refer to netlist.SimStrategy, netlist.SimState, etc., versus
# having to import directly from supporting modules.

from .SimStrategy import SimStrategy
from .SimState import SimState
from .KPIs import KPIs, netlist_createLogData, netlist_plotInstructions, netlist_rp_createLogData, netlist_rp_plotInstructions