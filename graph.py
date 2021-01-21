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
  print("getting uniswap tokens")
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
