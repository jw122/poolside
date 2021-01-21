import logging
import webapp2
from google.appengine.ext.webapp import template
from models import Token
import graph
from google.appengine.ext import db
import datetime
import json

class Index(webapp2.RequestHandler):
    def get(self):
        tokens = Token.all().fetch(50)
        context = { 'tokens': tokens }
        self.response.out.write(template.render('templates/index.html', context))


class UpdateData(webapp2.RequestHandler):
    def get(self):
        # top movers
        uniswap_tokens = fetch_uniswap()
        one_inch_tokens = fetch_one_inch()
        # new tokens
        new_listings = fetch_new()

        tokens = uniswap_tokens + one_inch_tokens + new_listings
        self.response.out.write('Saved %s tokens' % len(tokens))

class NewListingsAPI(webapp2.RequestHandler):
    def get(self):
        NEW_LISTING_MAX_DAYS = 5
        new_listing_cutoff = datetime.datetime.now() - datetime.timedelta(days=NEW_LISTING_MAX_DAYS)
        tokens = Token.all().filter('created > ', new_listing_cutoff).fetch(10)
        tokens.sort(reverse=True, key=lambda t: t.tradeVolume)
        api_response = {
            'tokens': [t.to_dict() for t in tokens]
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

class TopMoversAPI(webapp2.RequestHandler):
    def get(self):
        NEW_LISTING_MAX_DAYS = 5
        new_listing_cutoff = datetime.datetime.now() - datetime.timedelta(days=NEW_LISTING_MAX_DAYS)
        tokens = Token.all().order('-tradeVolume').fetch(10)
        api_response = {
            'tokens': [t.to_dict() for t in tokens]
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))


def fetch_one_inch():
    print("fetching data from 1inch")
    subgraph_response = graph.one_inch_tokens()
    tokens = []
    for token in subgraph_response['data']['tokens']:
        tokens.append(Token(key_name=token['id'],
        id=token['id'],
        name=token['name'],
        symbol=token['symbol'],
        tradeVolume=float(token['tradeVolume']),
        tradeCount=float(token['tradeCount']),
        decimals=int(token['decimals']),
        ))
    db.put(tokens)
    return tokens

def fetch_uniswap():
    print("fetching data from uniswap")
    subgraph_response = graph.uniswap_tokens()
    tokens = []
    for token_data in subgraph_response['data']['tokenDayDatas']:
        token = token_data['token']
        tokens.append(Token(key_name=token['id'],
        id=token['id'],
        name=token['name'],
        symbol=token['symbol'],
        price=float(token_data['priceUSD']),
        tradeVolume=float(token_data['dailyVolumeUSD']),
        tradeCount=float(token_data['dailyTxns']),
        decimals=int(token['decimals']),
        ))
    db.put(tokens)
    return tokens

def fetch_new():
    print("fetching new listings from uniswap")
    subgraph_response = graph.uniswap_new_tokens()
    tokens = []
    for token_data in subgraph_response['data']['pairs']:
        token0 = token_data['token0']
        token1 = token_data['token1']
        reserve0 = token_data['reserve0']
        reserve1 = token_data['reserve1']
        newest_token = token0
        price = token_data['token0Price']

        # TODO: confirm
        # usually the one with the lower reserve is the newer token in the pair
        if reserve0 < reserve1:
            newest_token = token1
            price = token_data['token1Price']

        print("newest token: ", newest_token)

        tokens.append(Token(key_name=newest_token['id'],
        id=newest_token['id'],
        name=newest_token['name'],
        symbol=newest_token['symbol'],
        price=float(price),
        tradeVolume=float(newest_token['tradeVolumeUSD']),
        tradeCount=float(newest_token['txCount']),
        decimals=int(newest_token['decimals']),
        created=datetime.datetime.fromtimestamp(float(token_data['createdAtTimestamp']))
        ))
    db.put(tokens)
    return tokens


def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Not found.')
    response.set_status(404)


application = webapp2.WSGIApplication([
    ('/', Index),
    ('/update-data', UpdateData),
    ('/api/new-listings', NewListingsAPI),
    ('/api/top-movers', TopMoversAPI),
], debug=True)
application.error_handlers[404] = handle_404
