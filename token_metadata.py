from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import model

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

api_key = model.get_setting('CMC_API_KEY')

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': api_key,
}

def get_metadata(symbol):
  session = Session()
  session.headers.update(headers)
  parameters = {
    'symbol': symbol
  }
  
  try:
    print("fetching info for " + symbol)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    if data['status']['error_message']:
      print("ERROR FETCHING FROM CMC: ", data['status']['error_message'])
    return data
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
