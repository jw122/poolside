import logging
import webapp2
from google.appengine.ext.webapp import template
from model import Token, Pair, Aavegotchi, ascii_printable, get_setting
import graph
import one_inch
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
            'pairs': [p.to_dict() for p in filter_pairs(pairs)]
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

class OneInchHandler(webapp2.RequestHandler):
    def get(self, token1_id, token2_id, amount):
        print("getting 1inch quote for pair {}-{} of amount {}".format(token1_id, token2_id, amount))
        api_response = one_inch.one_inch_quotes(token1_id, token2_id, amount)
        print("response from 1inch: ", api_response)
        to_token_amount = api_response['toTokenAmount']
        to_token = api_response['toToken']['symbol']
        from_token = api_response['fromToken']['symbol']
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'quotes': {'from_token': from_token, 'to_token': to_token, 'from_token_amount': amount, 'to_token_amount': to_token_amount}}))
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
        setattr(pair, self.request.get('action'), True)
        pair.put()
        api_response = {
            'pair': pair.to_dict()
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(api_response))

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

    for token in subgraph_response['data']['tokens']:
        symbol = token['symbol']
        new_token = Token(
            key_name=(token['id']),
            id=token['id'],
            name=token['name'],
            symbol=symbol,
            tradeVolume=float(token.get('tradeVolumeUSD',0)),
            tradeCount=int(token.get('txCount',0)),
            decimals=int(token['decimals']),
        )

        tokens.append(new_token)

    populate_metadata(tokens)
    db.put(tokens)
    return tokens

def populate_metadata(tokens):
        cmc_api_key = get_setting('CMC_API_KEY')
        symbols = [tok.symbol for tok in tokens if tok.symbol.isalnum() and tok.symbol.upper() not in token_metadata.invalid_tokens]

        symbol_query = ','.join(symbols)
        print("fetching CMC data for tokens with query: %s" % symbol_query)

        metadata, price_info = token_metadata.get_metadata(symbol_query, cmc_api_key)

        if metadata and 'data' in metadata:
            data = metadata['data']
            for token_symbol in data:
                info = data[token_symbol]
                if not info.get('platform'):
                    continue
                address = info['platform']['token_address']
                for token in tokens:
                    if token.id == address:
                        populate_token_metadata(info, price_info, token)
                        continue
                logging.warning('token not found for address: %s' % address)
        else:
            logging.warning('no metadata available')

def populate_token_metadata(info, price_info, token):


        logging.info("updating token: %s. info: %s" % (token.name, info))

        token.logo = info['logo']
        token.tags = info.get('tag-names') or []
        token.description = info['description']
        if len(info['urls']['website']) > 0:
            token.website = info['urls']['website'][0]
        if len(info['urls']['technical_doc']) > 0:
            token.whitepaper = info['urls']['technical_doc'][0]
        if len(info['urls']['twitter']) > 0:
            token.twitter = info['urls']['twitter'][0]
        if len(info['urls']['explorer']) > 0:
            token.explorer_url = info['urls']['explorer'][0]

        # price info
        if price_info['data'].get(token.symbol.upper()):
            quote = price_info['data'][token.symbol.upper()]['quote']['USD']
            logging.info("quote for token %s: %s" % (token.name, quote))
            if quote['price']:
                token.price = quote['price']
            if quote['percent_change_24h']:
                token.price_change_24h = quote['percent_change_24h']
            if quote['volume_24h']:
                token.volume_24h = quote['volume_24h']
        else:
            logging.warning('quote for token %s not found' % token.name)

        logging.info("updated details for token %s" % token.name)

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

def filter_pairs(pairs):
    def pairFilter(pair):
        if pair.confirmedScam:
            return False
        return True
    return [pair for pair in pairs if pairFilter(pair)]

def filter_top_movers(tokens):
    def tokenFilter(token):
        if token.symbol in ['WETH', 'USDC', 'USDT', 'DAI', 'WBTC']:
            # filter out tokens that are always highest in volume
            return False
        # this is a temporary patch to handle some tokens not having price set
        if not token.price:
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
    webapp2.Route(r'/api/one-inch/<token1_id>-<token2_id>-<amount>', handler=OneInchHandler, name='token_ids'),
    webapp2.Route('/api/search', SearchAPI),
    webapp2.Route('/admin/admin-action', AdminAction),
], debug=True)
application.error_handlers[404] = handle_404
