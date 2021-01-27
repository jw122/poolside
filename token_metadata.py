from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import model
import logging

metadata_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
price_quotes_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

api_key = model.get_setting('CMC_API_KEY')

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': api_key,
}

def get_metadata(symbol):
  if not api_key:
      logging.error('CMC_API_KEY setting is missing. Cannot fetch metadata.')
      return
  session = Session()
  session.headers.update(headers)
  parameters = {
    'symbol': symbol
  }

  try:
    print("fetching info for " + symbol)
    metadata = session.get(metadata_url, params=parameters)
    price_info = session.get(price_quotes_url, params=parameters)
    
    metadata_json = json.loads(metadata.text)
    price_json = json.loads(price_info.text)
    if metadata_json['status']['error_message']:
      print("ERROR FETCHING FROM CMC: ", metadata_json['status']['error_message'])
    return metadata_json, price_json
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
