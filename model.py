import logging
from google.appengine.ext import db
import math
import string

def ascii_printable(s):
    _VISIBLE_PRINTABLE_ASCII = frozenset(
    set(string.printable) - set(string.whitespace))
    return ''.join([c for c in s if c in _VISIBLE_PRINTABLE_ASCII])

def token_from_pair_name(n):
    return n.replace('Wrapped Ether, ', '').replace(', Wrapped Ether', '')

def token_from_pair_symbol(n):
    return n.replace('WETH-', '').replace('-WETH', '')

class Model():
    def to_dict(self):
       return dict([(p, unicode(getattr(self, '%s_to_dict' % p, getattr(self, p)))) for p in self.properties()])

class TokenModel(Model):

    @property
    def tradeVolume_to_dict(self):
        if self.tradeVolume > 1000000:
            return '%sM' %  math.floor(self.tradeVolume/1000000)
        if self.tradeVolume > 10000:
            return '%sk' %  math.floor(self.tradeVolume/1000)
        elif self.tradeVolume:
            return '%s' % self.tradeVolume
        else:
            return ''

class Token(db.Expando, TokenModel):
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




class Pair(db.Expando, TokenModel):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    tradeCount = db.FloatProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)

    def to_dict(self):
        pair_dict = super(Pair, self).to_dict()
        pair_dict['pair-name'] = pair_dict['name']
        pair_dict['name'] =  token_from_pair_name(pair_dict['name'])
        pair_dict['pair-symbol'] =  token_from_pair_symbol(pair_dict['symbol'])
        pair_dict['symbol'] = pair_dict['symbol']
        return pair_dict
