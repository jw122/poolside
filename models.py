import logging
from google.appengine.ext import db
import math

class Model():
    def to_dict(self):
       return dict([(p, unicode(getattr(self, '%s_to_dict' % p, getattr(self, p)))) for p in self.properties()])

class Token(db.Expando, Model):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    description = db.StringProperty(required=False)
    price = db.FloatProperty(required=False)
    tradeCount = db.FloatProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    decimals = db.IntegerProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)


    @property
    def tradeVolume_to_dict(self):
        if self.tradeVolume > 10000:
            return '%sk' %  math.floor(self.tradeVolume/1000)
        elif self.tradeVolume:
            return '%s' % self.tradeVolume
        else:
            return ''

class Pair(db.Expando, Model):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    tradeCount = db.FloatProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)

    def to_dict(self):
        logging.info('to dict')
        pair_dict = super(Pair, self).to_dict()
        pair_dict['pair-name'] = pair_dict['name']
        pair_dict['name'] = pair_dict['name'].replace('Wrapped Ether, ', '').replace(', Wrapped Ether', '')
        pair_dict['pair-symbol'] = pair_dict['symbol']
        pair_dict['symbol'] = pair_dict['symbol'].replace('WETH-', '').replace('-WETH', '')
        return pair_dict
