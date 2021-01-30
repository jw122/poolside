import logging
import requests

REQUEST_TIMEOUT = 15

def one_inch_quotes(token1, token2, amount):
    headers = {}
    query = 'https://api.1inch.exchange/v2.0/quote?fromTokenAddress={}&toTokenAddress={}&amount={}'.format(token1, token2, amount)
    print("querying 1inch: ", query)
    request = requests.get(query, headers=headers, timeout=REQUEST_TIMEOUT)
    if request.status_code == 200:
        return request.json()
