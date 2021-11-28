# TokenSPICE for Science Token Communities

This is an overview of how Opscientia is using TokenSPICE for simulations of science token communities. It contains inoformation on how to run the existing simulations on your own machine, description of the agents and models, and a list of features open to contributors.

Firstly, make follow the setup guide in the main README. There are currently six netlists simulating different science value flows. The description of the different models can be found in `assets/netlists/opsci_naive/`, `assets/netlists/opsci_profit_sharing/` (contains information about profit_sharing, mult_profit_sharing, and mult_time_profit_sharing models), `assets/netlists/opsci_public_funding_ps/`.

Before running simulations, make sure to create a new folder to save your data into. Here, we assume a local folder named `simulation_data/` with `csv/` and `png/` folders within it. Below is a list of commands to run the simulations:

1. Baseline model

Netlist code available at `assets/netlists/opsci_naive/`, agents `assets/agents/opsci_agents/` and `assets/agents/opsci_agents/profit_sharing_agents`. Fixed netlist, for changing parameters, you'll need to change `assets/netlists/opsci_naive/SimState.py`.

- run: `tsp run assets/netlists/opsci_naive/netlist.py simulation_data/csv/opsci_naive_01`
- plot: `tsp plot assets/netlists/opsci_naive/netlist.py simulation_data/csv/opsci_naive_01 simulation_data/png/opsci_naive_01`

2. Profit Sharing model

Netlist code available at `assets/netlists/opsci_profit_sharing/`, agents `assets/agents/opsci_agents/profit_sharing_agents`. To change simulation parameters, you'll need to change the constants at `assets/netlists/opsci_profit_sharing/SimStrategy.py`. Relevant parameters include: `TICKS_BETWEEN_PROPOSALS`,`PRICE_OF_ASSETS`, `RATIO_FUNDS_TO_PUBLISH`, `TRANSACTION_FEES`, `FEES_TO_STAKERS`, `NUMBER_OF_RESEARCHERS`, `FUNDING_BOUNDARY`.

- run: `tsp run assets/netlists/opsci_profit_sharing/netlist.py simulation_data/csv/opsci_profit_sharing_01`
- plot: `tsp plot assets/netlists/opsci_profit_sharing/netlist.py simulation_data/csv/opsci_profit_sharing_01 simulation_data/png/opsci_profit_sharing_01`

3. Multiple Proposal Profit Sharing model

Netlist code available at `assets/netlists/opsci_mult_profit_sharing/`, agents `assets/agents/opsci_agents/mult_agents`. To change simulation parameters, you'll need to change the constants at `assets/netlists/opsci_mult_profit_sharing/SimStrategy.py`. Relevant parameters include: `TICKS_BETWEEN_PROPOSALS`,`PRICE_OF_ASSETS`, `RATIO_FUNDS_TO_PUBLISH`, `TRANSACTION_FEES`, `FEES_TO_STAKERS`, `NUMBER_OF_RESEARCHERS`, `FUNDING_BOUNDARY`, `PROPOSALS_FUNDED_AT_A_TIME`. Note: If you want to use `PROPOSAL_SETUP`, add it to the researchers in `SimState.py`.

- run: `tsp run assets/netlists/opsci_mult_profit_sharing/netlist.py simulation_data/csv/opsci_mult_profit_sharing_01`
- plot: `tsp plot assets/netlists/opsci_mult_profit_sharing/netlist.py simulation_data/csv/opsci_mult_profit_sharing_01 simulation_data/png/opsci_mult_profit_sharing_01`

4. Multiple Proposal Rolling Basis Funding Profit Sharing model

Netlist code available at `assets/netlists/opsci_mult_time_profit_sharing/`, agents `assets/agents/opsci_agents/mult_time_agents`. To change simulation parameters, you'll need to change the constants at `assets/netlists/opsci_mult_time_profit_sharing/SimStrategy.py`. Relevant parameters include: `PRICE_OF_ASSETS`, `RATIO_FUNDS_TO_PUBLISH`, `TRANSACTION_FEES`, `FEES_TO_STAKERS`, `NUMBER_OF_RESEARCHERS`, `FUNDING_BOUNDARY`, `PROPOSALS_FUNDED_AT_A_TIME`, `RANDOM_BUYING`. Note: If you want to use `PROPOSAL_SETUP`, add it to the researchers in `SimState.py`; if `RANDOM_BUYING = True`, researchers will randomly buy assets from the knowledge market, causing significant fluctuations in data.

- run: `tsp run assets/netlists/opsci_mult_time_profit_sharing/netlist.py simulation_data/csv/opsci_mult_time_profit_sharing_01`
- plot: `tsp plot assets/netlists/opsci_mult_time_profit_sharing/netlist.py simulation_data/csv/opsci_mult_time_profit_sharing_01 simulation_data/png/opsci_mult_time_profit_sharing_01`

5. Public Funding Profit Sharing model

Netlist code available at `assets/netlists/opsci_public_funding_ps/`, agents `assets/agents/opsci_pp_agents/`. To change simulation parameters, you'll need to change the constants at `assets/netlists/opsci_public_funding_ps/SimStrategy.py`. Relevant parameters include: `PRICE_OF_ASSETS`, `RATIO_FUNDS_TO_PUBLISH`, `TRANSACTION_FEES`, `FEES_TO_STAKERS`, `NUMBER_OF_RESEARCHERS`, `FUNDING_BOUNDARY`, `PROPOSALS_FUNDED_AT_A_TIME`, `PRIVATE_PUBLISH_COST`, `ASSET_COSTS`. Note: If you want to use `PROPOSAL_SETUP`, add it to the researchers in `SimState.py`.

- run: `tsp run assets/netlists/opsci_public_funding_ps/netlist.py simulation_data/csv/opsci_public_funding_ps_01`
- plot: `tsp plot assets/netlists/opsci_public_funding_ps/netlist.py simulation_data/csv/opsci_public_funding_ps_01 simulation_data/png/opsci_public_funding_ps_01`

6. Public Funding Profit Sharing model with Community Growth

Netlist code available at `assets/netlists/growth_public_funding_ps/`, agents `assets/agents/opsci_pp_agents/`. To change simulation parameters, you'll need to change the constants at `assets/netlists/growth_public_funding_ps/SimStrategy.py`. Relevant parameters include: `PRICE_OF_ASSETS`, `RATIO_FUNDS_TO_PUBLISH`, `TRANSACTION_FEES`, `FEES_TO_STAKERS`, `NUMBER_OF_RESEARCHERS`, `FUNDING_BOUNDARY`, `PROPOSALS_FUNDED_AT_A_TIME`, `PRIVATE_PUBLISH_COST`, `ASSET_COSTS`. Note: If you want to use `PROPOSAL_SETUP`, add it to the researchers in `SimState.py`. The main addition to this netlist is the `ReseracherGeneratorAgent`. To change the growth function and condition for the generator, change `generator_cond_type`, `generator_type`, `time_interval`, and `start_gen` in `SimState.py` in the `ResearcherGeneratorAgent`.

- run: `tsp run assets/netlists/growth_public_funding_ps/netlist.py simulation_data/csv/opsci_public_funding_ps_01`
- plot: `tsp plot assets/netlists/opsci_public_funding_ps/netlist.py simulation_data/csv/opsci_public_funding_ps_01 simulation_data/png/opsci_public_funding_ps_01`


## Future contributions

For anyone interested in expanding the functionality of TokenSPICE for open science, here is a list of netlists and features that would be helpful.

- SourceCred implementation for higher level resolution of community contributions
- peer review actions and rewards for researchers
- quadratic funding model
- token ecosystem with a minter (tracking supply, price, different reward distribution experiments)