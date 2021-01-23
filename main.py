import logging
import webapp2
from google.appengine.ext.webapp import template
from models import Token, Pair
import graph
from google.appengine.ext import db
import datetime
import json

class Index(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/index.html', {}))


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
        pairs = Pair.all().filter('created > ', new_listing_cutoff).order('-created').fetch(10)
        api_response = {
            'pairs': [p.to_dict() for p in pairs]
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
        tradeCount=int(token['tradeCount']),
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
        tradeCount=int(token_data['dailyTxns']),
        decimals=int(token['decimals']),
        ))
    db.put(tokens)
    return tokens

def fetch_new():
    print("fetching new listings from uniswap")
    subgraph_response = graph.uniswap_new_tokens()
    pairs = []
    for pair in subgraph_response['data']['pairs']:
        token0 = pair['token0']
        token1 = pair['token1']

        pair_symbol = token0['symbol'] + '-' + token1['symbol']
        pair_name = token0['name'] + ', ' + token1['name']
        print("getting pair: ", pair_name)

        pairs.append(Pair(key_name=pair_symbol,
        id=pair['id'],
        symbol=pair_symbol,
        name=pair_name,
        tradeVolume=float(pair['volumeUSD']),
        tradeCount=int(pair['txCount']),
        created=datetime.datetime.fromtimestamp(float(pair['createdAtTimestamp']))
        ))
    db.put(pairs)
    return pairs


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
