import logging
import webapp2
from google.appengine.ext.webapp import template
from model import Token, Pair, Aavegotchi, ascii_printable, get_setting
import graph
import token_metadata
import search
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import datetime
import time
import json
import os

class Index(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/index.html', {
            'isAdmin': self.request.path == '/admin'
        }))


class UpdateData(webapp2.RequestHandler):
    def get(self):
        # top movers
        uniswap_tokens = fetch_uniswap()

        # NOTE: temporarily commented out since we're using uniswap for top movers
        # one_inch_tokens = fetch_one_inch()

        # new tokens
        new_listings = fetch_new()

        token_names = []
        documents = []
        for token_list in [new_listings, uniswap_tokens]:
            for token in token_list:
                logging.info('token key name: %s' % token.key().name())
                if token.key().name() not in token_names:
                    token_names.append(token.key().name())
                    search_fields = [
                        { 'name': 'name', 'value': token.name.split(',')[0], 'tokenize': True },
                        { 'name': 'symbol', 'value': token.symbol, 'tokenize': False  },
                    ]
                    documents.append(search.create_document(token.key().name(), search_fields))
                else:
                    logging.warning('token document already created: %s' % token.key().name())

        MAX_DOCUMENTS = 200
        if documents:
            for x in xrange(0,len(documents),MAX_DOCUMENTS):
                search.add_documents_to_index('tokens', documents[x:x+MAX_DOCUMENTS])

        tokens = uniswap_tokens + new_listings
        self.response.out.write('Saved %s tokens' % len(tokens))

class UpdateNFTData(webapp2.RequestHandler):
    def get(self):
        # top movers
        fetch_aavegotchis()

class NewListingsAPI(webapp2.RequestHandler):
    def get(self):
        NEW_LISTING_MAX_DAYS = 5
        new_listing_cutoff = datetime.datetime.now() - datetime.timedelta(days=NEW_LISTING_MAX_DAYS)
        pairs = Pair.all().filter('created > ', new_listing_cutoff).order('-created').fetch(500)
        api_response = {
            'pairs': [p.to_dict() for p in pairs]
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

class TopMoversAPI(webapp2.RequestHandler):
    def get(self):
        tokens = Token.all().order('-tradeVolume').fetch(500)
        api_response = {
            'tokens': [t.to_dict() for t in filter_top_movers(tokens)]
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

class AavegotchisAPI(webapp2.RequestHandler):
    def get(self):
        aavegotchis = Aavegotchi.all().order('-created').fetch(100)
        api_response = {
            'aavegotchis': [t.to_dict() for t in aavegotchis]
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

class TokenAPI(webapp2.RequestHandler):
    def get(self, token_id):
        token = Token.get_by_key_name(token_id)
        api_response = {
            'token': token.to_dict()
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/token_details.html')
        self.response.out.write(template.render(path, {'token': token}))


class SearchAPI(webapp2.RequestHandler):
    def get(self):
        documents = search.query_index('tokens', self.request.get('keyword'))
        if documents:
            tokens = [t.to_dict() for t in Token.get_by_key_name([document.doc_id for document in documents]) if t]
            tokens.extend([t.to_dict() for t in Pair.get_by_key_name([document.doc_id for document in documents]) if t])
        else:
            tokens = []
        api_response = {
            'tokens': tokens
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

class AdminAction(webapp2.RequestHandler):
    def post(self):
        pair = Pair.get_by_key_name(self.request.get('pair'))
        if self.request.get('action') == 'hasAnonymousTeam':
            pair.hasIdentifiedTeam = False
        else:
            setattr(pair, self.request.get('action'), True)
        pair.put()

def fetch_one_inch():
    print("fetching data from 1inch")
    subgraph_response = graph.one_inch_tokens()
    tokens = []
    for token in subgraph_response['data']['tokens']:
        tokens.append(Token(key_name=ascii_printable(token['id']),
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
    cmc_api_key = get_setting('CMC_API_KEY')
    for token in subgraph_response['data']['tokens']:
        symbol = token['symbol']
        new_token = Token(
            key_name=(token['id']),
            id=token['id'],
            name=token['name'],
            symbol=symbol,
            # TODO: this is not available through uniswap. get it elsewhere
            # price=float(token_data.get('priceUSD', 0)),
            tradeVolume=float(token.get('tradeVolumeUSD',0)),
            tradeCount=int(token.get('txCount',0)),
            decimals=int(token['decimals']),
        )

        # TODO: only get metadata if not already in DB

        metadata, price_info = token_metadata.get_metadata(symbol, cmc_api_key)

        if price_info and 'data' in price_info:
            if symbol.upper() in price_info['data']:
                quote = price_info['data'][symbol.upper()]['quote']['USD']
                if quote['price']:
                    new_token.price = quote['price']
                if quote['percent_change_24h']:
                    new_token.price_change_24h = quote['percent_change_24h']
                if quote['volume_24h']:
                    new_token.volume_24h = quote['volume_24h']
        if metadata and 'data' in metadata:
            print("processing data for ", symbol)
            if symbol.upper() in metadata['data']:
                info = metadata['data'][symbol.upper()]
                print("got info from CMC", info)
                logging.info(info)

                new_token.logo = info['logo']
                new_token.tags = info.get('tag-names') or []
                new_token.description = info['description']
                if len(info['urls']['website']) > 0:
                    new_token.website = info['urls']['website'][0]
                if len(info['urls']['technical_doc']) > 0:
                    new_token.whitepaper = info['urls']['technical_doc'][0]
                if len(info['urls']['twitter']) > 0:
                    new_token.twitter = info['urls']['twitter'][0]
                if len(info['urls']['explorer']) > 0:
                    new_token.explorer_url = info['urls']['explorer'][0]
            new_token.created = datetime.datetime.strptime(info['date_added'], "%Y-%m-%dT%H:%M:%S.%fZ")
            time.sleep(2)

        tokens.append(new_token)
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
        if scam_filter(pair):
            print("scam detected! Skipping pair", pair_symbol)
            continue

        print("creating getting pair: ", pair_name)

        pairs.append(Pair(key_name=ascii_printable(pair_symbol),
        id=pair['id'],
        symbol=pair_symbol,
        name=pair_name,
        tradeVolume=float(pair['volumeUSD']),
        tradeCount=int(pair['txCount']),
        created=datetime.datetime.fromtimestamp(float(pair['createdAtTimestamp']))
        ))
    if pairs:
        db.put(pairs)
    return pairs


def fetch_aavegotchis():
    subgraph_response = graph.aavegotchi_core_kovan()
    aavegotchis = []
    for aavegotchi in subgraph_response['data']['aavegotchis']:
        aavegotchis.append(Aavegotchi(
            key_name=aavegotchi['id'],
            id=aavegotchi['id'],
            name=aavegotchi['name'],
            kinship=aavegotchi['kinship'],
            rarityScore=aavegotchi['rarityScore'],
        ))
    if aavegotchis:
        db.put(aavegotchis)
        logging.info('saved %s aavegotchis' % len(aavegotchis))
    return aavegotchis


def scam_filter(listing):
    tx_count = int(listing['txCount'])
    volume_usd = float(listing['volumeUSD'])
    if tx_count < 100 or volume_usd < 1:
        return True
    return False

def filter_top_movers(tokens):
    def tokenFilter(token):
        if token.symbol in ['WETH', 'USDC', 'USDT', 'DAI', 'WBTC']:
            # filter out tokens that are always highest in volume
            return False
        return True
    return [token for token in tokens if tokenFilter(token)]



def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Not found.')
    response.set_status(404)


application = webapp2.WSGIApplication([
    webapp2.Route('/', Index),
    webapp2.Route('/admin', Index),
    webapp2.Route('/update-data', UpdateData),
    webapp2.Route('/update-nft-data', UpdateNFTData),
    webapp2.Route('/api/new-listings', NewListingsAPI),
    webapp2.Route('/api/top-movers', TopMoversAPI),
    webapp2.Route('/api/aavegotchis', AavegotchisAPI),
    webapp2.Route(r'/api/token/<token_id>', handler=TokenAPI, name='token_id'),
    webapp2.Route('/api/search', SearchAPI),
    webapp2.Route('/admin/admin-action', AdminAction),
], debug=True)
application.error_handlers[404] = handle_404
