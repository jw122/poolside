import logging
import requests

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
        json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
