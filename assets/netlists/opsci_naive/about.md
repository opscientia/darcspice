# Open Science Token Ecosystem
This simulation is testing the longevity of a decentralized open science ecosystem where researchers receive grants, buy data, and publish papers.

![](opsci_naive.jpeg)

Note: throughout this project, the term *asset* is used solely within the context of the Opscientia marketplace, hence it encompasses data, algorithms, computing power, storage, and research papers.

### KPIs

The key metrics measured in this simulation are: 
- number of assets in the marketplace
- number of sellers (corresponding to the number of researchers who have finished their work and continue to be compensated for it)
- amount of OCEAN
- price of OCEAN
- monthly revenue of sellers

### List of Agents
- ```ResearcherAgent```
- ```RouterAgent```
- ```OpsciMarketPlaceAgent```
- ```SellerAgent```
- ```OCEANBurnerAgent```
- ```OCEANMinterAgent```
- ```OpscientiaDAOAgent``` (Token Treasury above)
- ```ProposalStorageAgent``` (Research Funding Marketplace above)

### Description of one step in the loop

1. ```ResearcherAgent``` publishes a grant proposal (fixed price)
2. ```OCEANMinterAgent``` mints fixed amount of OCEAN and sends it to ```RouterAgent```
3. ```RouterAgent``` sends the requested amount of OCEAN to ```ResearcherAgent```
4. ```ResearcherAgent``` sends fixed amount of OCEAN to ```OpsciMarketplaceAgent``` and the rest is burned (work done)
5. ```OpsciMarketplaceAgent``` sends all OCEAN evenly to all instances of ```SellerAgent``` and sends a fixed ratio to ```OCEANBurnerAgent``` (equivalent to a partial ownership of the research assets by the DAO)
6. ```OCEANBurnerAgent``` spends everything in its wallet
7. ```ResearcherAgent``` "publishes" *assets* to ```OpsciMarketplaceAgent``` (corresponding to ```assets += 1```)
8. New ```SellerAgent``` is created (corresponding to a researcher selling *assets* from research)

The diagram above shows a researcher minter, however, it will be easier if we only create a new ```SellerAgent``` rather than destroy the existing ```ResearcherAgent```, then create a new ```SellerAgent```, and then a new ```ResearcherAgent```.

### Limitations of this model

Since this is a naive implementation of the open science token ecosystem, it is bound to be restricted in its precise representation of true open science market behavior. Here is a short list of the identified limitations:
- fixed number of researchers, grant size, project length, and asset output size (not reflecting the real-world variability of research projects, which usually have teams of multiple people actively working for long periods of time)
- fixed price for marketplace assets (clearly, different services will have different prices, datasets may vary in size, algorithms may vary in the price for their utility)
- even distribution of funds to asset sellers (this will result in a gradual decrease in revenue/seller (since the money flowing through the marketplace is constant), which is on one hand slightly representative of the scenario where more people are selling their assets, thus increasing the competition and supply, hence lowering revenue, but on the other, it fails to represent the variability of different assets offered)

### Future improvements of the model

To successfully simulate a realistic open science environment, we need to add randomness to some fixed variables such as the research size, number of researchers, cost of assets, etc. Furthermore, we can make use of DataTokens and DataWallets to track different types of assets in the open science marketplace.

Let's consider a simple grant model (omitting DeSci):
1. A research grant proposal is submitted by a research team/
2. The proposal is evaluated by a grant agency.
3. If the grant has merit (determined by the properties of the proposal), the grant is accepted.
Note: The grant will only be used to cover the required expenses for the research project. In the case of universities, professors receive a fixed salary from the university and the grant is only there to support their research project.
4. The research team spends all grant money on equipment, data acquisition, computing power, etc., and writes a research paper.
5. The research paper has some impact and continues to deliver value after the research is finished (e.g. data, algorithms, citations, etc.).
6. The grant agency receives a portion of this additional value (for providing the grant in the first place) and part of the value goes to the research team (for doing the work).
7. The researchers in the research team get some “reputation points” based on the value of their research and their contributions (“reputation points” may be a factor at play for getting additional grants in the future).

To address point 3, we can create a list of parameters in a grant proposal that might intuitively be indicators of a worthwhile research project. All of these parameters can then serve as input to an evaluator function which will determine whether a proposal will be accepted (this is still a rather naive model, since in a fully decentralized ecosystem, the release of grants should be determined by the community, however, this approach can still be utilized as an indication of merit).

These parameters may include: number of researchers, timeframe, grant size, reputation of researchers, number of deliverables, timeframe for deliverables.

Reputation of researchers can itself be a return value of a multivariable function, with inputs such as: number of research papers published, previous contribution in projects, number of citations, number of algorithms/data bought by the community in the open science marketplace, etc. Contribution can be measured with something like [SourceCred](https://sourcecred.io/).