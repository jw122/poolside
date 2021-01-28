import logging
import requests

REQUEST_TIMEOUT = 15

def one_inch_quotes(token1, token2):
    headers = {}
    query = 'https://api.1inch.exchange/v2.0/quote?fromTokenAddress={}&toTokenAddress={}&amount=1'.format(token1, token2)

    request = requests.get(query, headers=headers, timeout=REQUEST_TIMEOUT)
    if request.status_code == 200:
        return request.json()
