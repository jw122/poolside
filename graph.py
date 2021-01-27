import logging
import requests

GRAPH_REQUEST_TIMEOUT = 15

def one_inch_tokens(count=50):
    headers = {}
    query = """
    {
      tokens(first: %(count)s) {
        id
        symbol,
        name,
        decimals,
        tradeVolume,
        tradeCount,
      }
    }
    """ % { 'count': count }
    request = requests.post('https://api.thegraph.com/subgraphs/name/1inch-exchange/one-inch-v2',
        json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
    if request.status_code == 200:
        return request.json()

def uniswap_tokens(count=20):
  print("getting uniswap tokens")
  headers = {}
  query = """
  {

    tokens(first: %(count)s, orderBy:tradeVolumeUSD, orderDirection:desc) {
      id
      symbol
      name
      decimals
      tradeVolumeUSD
      txCount
    }
  }
  """ % { 'count': count }

  request = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
      json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
  if request.status_code == 200:
      return request.json()



def uniswap_new_tokens(count=50):
  headers = {}
  query = """
  {
      pairs(first:%(count)s, orderBy:createdAtTimestamp, orderDirection:desc) {
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
        id
        reserve0
        reserve1
        volumeToken0
        volumeToken1
        token0Price
        token1Price
        totalSupply
        reserveUSD
        volumeUSD
        txCount
        createdAtTimestamp
      }
  }
  """ % { 'count': count }

  request = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
      json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
  if request.status_code == 200:
      return request.json()


def aavegotchi_core_kovan(count=50):
  headers = {}
  query = """
  {
  aavegotchis(first: %(count)s) {
    id
    kinship
    name
    rarityScore
  }
  }
  """ % { 'count': count }

  request = requests.post('https://api.thegraph.com/subgraphs/name/aavegotchi/aavegotchi-core-kovan',
      json={'query': query}, headers=headers, timeout=GRAPH_REQUEST_TIMEOUT)
  if request.status_code == 200:
      return request.json()
