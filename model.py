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
        properties = []
        for p in self.properties():
            value = getattr(self, '%s_to_dict' % p, getattr(self, p))
            value_tuple = (p, unicode(value) if value else None)
            properties.append(value_tuple)
        entity = dict(properties)
        entity['keyName'] = self.key().name()
        return entity


class TokenModel(Model):

    @property
    def tradeVolume_to_dict(self):
        return volume_to_dict(self.tradeVolume)

    @property
    def volume_24h_to_dict(self):
        return volume_to_dict(self.volume_24h)

    @property
    def price_to_dict(self):
        return round(self.price, 2) if self.price else None

    @property
    def price_change_24h_to_dict(self):
        return round(self.price_change_24h or 0, 1) if self.price_change_24h else None

def volume_to_dict(volume):
    if volume > 1000000:
        return '%sM' %  math.floor(volume/1000000)
    if volume > 10000:
        return '%sk' %  math.floor(volume/1000)
    elif volume:
        return '%s' % int(volume)
    else:
        return ''

class Token(db.Expando, TokenModel):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    description = db.StringProperty(required=False)
    price = db.FloatProperty(required=False)
    price_change_24h = db.FloatProperty(required=False)
    volume_24h = db.FloatProperty(required=False)
    tradeCount = db.IntegerProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    decimals = db.IntegerProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)

    website = db.StringProperty(required=False)
    logo = db.StringProperty(required=False)
    whitepaper_url = db.StringProperty(required=False)
    twitter = db.StringProperty(required=False)
    explorer_url = db.StringProperty(required=False)

    def to_dict(self):
        token_dict = super(Token, self).to_dict()
        MAX_DESCRIPTION_LENGTH = 40;

        description = token_dict.get('description') or ''
        token_dict['truncatedDescription'] = '%s...' % description[0:MAX_DESCRIPTION_LENGTH] if len(description) > MAX_DESCRIPTION_LENGTH else description

        price_change = self.price_change_24h
        token_dict['priceChangeClass'] = {
            'text-green-300': 0 <= price_change < 3,
            'text-green-400': 3 <= price_change < 6,
            'text-green-500': 6 <= price_change < 10,
            'text-green-700': price_change > 10,
            'text-red-300': 0 >= price_change > -3,
            'text-red-400': -3 >= price_change > -6,
            'text-red-500': -6 >= price_change > -10,
            'text-red-700': price_change < -10,
            'font-bold': price_change > 10 or price_change < -10
        }
        return token_dict



class Pair(db.Expando, TokenModel):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    tradeCount = db.IntegerProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)

    hasIdentifiedTeam = db.BooleanProperty(required=False)
    isLiquidityLocked = db.BooleanProperty(required=False)
    hasWebsite = db.BooleanProperty(required=False)
    hasInvestors = db.BooleanProperty(required=False)
    hasWhitepaper = db.BooleanProperty(required=False)
    isAudited = db.BooleanProperty(required=False)
    isClone = db.BooleanProperty(required=False)
    age = db.IntegerProperty(required=False) #  months?


    def to_dict(self):
        pair_dict = super(Pair, self).to_dict()
        pair_dict['pair-name'] = pair_dict['name']
        pair_dict['name'] =  token_from_pair_name(pair_dict['name'])
        pair_dict['pair-symbol'] =  token_from_pair_symbol(pair_dict['symbol'])
        pair_dict['symbol'] = pair_dict['symbol']
        pair_dict['addedDate'] = self.addedDate
        return pair_dict

    @property
    def addedDate(self):
        return self.created.strftime('%b %d')


class Aavegotchi(db.Expando, Model):
    # key_name is id
    id = db.StringProperty()
    name = db.StringProperty(required=False)
    kingship = db.StringProperty(required=False)
    rarityScore = db.StringProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)

class Setting(db.Expando):
    # key_name is id
    id = db.StringProperty()
    value = db.StringProperty(required=False)

def update_setting(id, value):
    setting = Setting.get_by_key_name(id)
    if not setting:
        setting = Setting(key_name=id, id=id)
    setting.value = value
    setting.put()
    return setting.value

def get_setting(id):
    setting = Setting.get_by_key_name(id)
    if setting:
        return setting.value
