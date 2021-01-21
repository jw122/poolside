import logging
import requests

GRAPH_REQUEST_TIMEOUT = 15

def one_inch_tokens():
    headers = {}
    query = """
    {
      tokens(first: 50) {
        id
        symbol,
        name,
        decimals,
        tradeVolume,
        tradeCount,
      }
    }
    """
    request = requests.post('https://api.thegraph.com/subgraphs/name/1inch-exchange/one-inch-v2',
        json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
    if request.status_code == 200:
        return request.json()

def uniswap_tokens():
  headers = {}
  query = """
  {

    tokenDayDatas(first: 50, orderBy:dailyVolumeUSD, orderDirection:desc) {
      id
      token {
        id
        symbol
        name
        decimals
        tradeVolumeUSD
        txCount
      }

      date
      totalLiquidityUSD
      dailyVolumeUSD
      dailyTxns
      priceUSD
    }
  }
  """

  request = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
      json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
  if request.status_code == 200:
      return request.json()

def uniswap_new_tokens():
  headers = {}
  query = """
  {
      pairs(first:20, orderBy:createdAtTimestamp, orderDirection:desc) {
        token0 {
          id
          symbol
          name
          decimals
          tradeVolumeUSD
          txCount
        }
        token1 {
          id
          symbol
          name
          decimals
          tradeVolumeUSD
          txCount
        }
        reserve0
        reserve1
        volumeToken0
        volumeToken1
        token0Price
        token1Price
        totalSupply
        reserveUSD
        createdAtTimestamp
      }
  }
  """

  request = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
      json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
  if request.status_code == 200:
      return request.json()