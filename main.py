import logging
import webapp2
from google.appengine.ext.webapp import template
from models import Token
import requests
from google.appengine.ext import db

class IndexHandler(webapp2.RequestHandler):
    def get(self):
        tokens = Token.all().fetch(50)
        context = { 'tokens': tokens }
        self.response.out.write(template.render('templates/index.html', context))


class LoadDataHandler(webapp2.RequestHandler):
    def get(self):
        headers = {}
        query = """
        {
          tokens(first: 50) {
            id
            symbol,
            name,
            decimals,
            tradeVolume,
          }
        }
        """
        request = requests.post('https://api.thegraph.com/subgraphs/name/1inch-exchange/one-inch-v2',
            json={'query': query}, headers=headers)
        if request.status_code == 200:
            response = request.json()
            tokens = []
            for token in response['data']['tokens']:
                tokens.append(Token(key_name=token['id'],
                id=token['id'],
                name=token['name'],
                symbol=token['symbol'],
                tradeVolume=float(token['tradeVolume']),
                decimals=int(token['decimals']),
                ))
            db.put(tokens)
            self.response.out.write('Saved %s tokens' % len(tokens))


class UpdateDataHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('this will be where data is updated via cron job')

def handle_404(request, response, exception):
    """Return a custom 404 error."""
    response.write('Not found.')
    response.set_status(404)


application = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/load-data', LoadDataHandler),
    ('/update-data', UpdateDataHandler),
], debug=True)
application.error_handlers[404] = handle_404
