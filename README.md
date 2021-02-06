# Poolside
Poolside is the source for new listings and trending assets in DeFi. Find and search through real-time data aggregated from The Graph, Uniswap, 1inch, Aavegotchi, Coinmarketcap and more.

Built by [James](https://jamslevy.github.io/) (james@poolside.finance) and [Julia](https://juliawu.me) (julia@poolside.finance) at the MarketMake hackathon. 

## About the Project
The first version of Poolside offers the following core features:

1. New listings from Uniswap with scam filtering (automated and manual curation)
2. Trending tokens (top movers based on volume) and quotes from 1inch
3. Basic NFT data (Aavegotchi)
4. Search

Users come to Poolside to discover the latest and promising tokens listed on Uniswap. As we fetch and index new listings, we also apply scam-filtering logic to eliminate the obvious fakes and clones. We also allow admins to manually flag tokens as scams. We believe that this form of curation can later become incentivized through PLSD tokens.

The top movers are ordered by trade volume. For each token, one can see the daily and all-time volumes, current price, and change in the past day.  The detailed view provides links to the token's website, whitepaper, and etherscan. 

What differentiates Poolside from existing landing pages such as Defi Pulse? 

1. Data is updated on regular intervals and ranked dynamically, not static
2. Scam-filtering
3. Search functionality
4. Wallet integration for personalized results.

## What's Next? 

We plan to take Poolside further with personalization, integrations with news and  scam-filtering token lists, and detection of noteworthy events in the markets. We also plan to continue indexing data from even more sources and types (NFT, Token Sets).


# Run Locally

1. Clone this repo
2. Install `gcloud` if it is not already installed.
3. In the parent directory containing this project, run `dev_appserver.py poolside`
4. Go to http://localhost:8080/update-data to load initial data into the database.
5. Go to http://localhost:8080/ to view previously loaded data
