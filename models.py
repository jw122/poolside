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
    tradeCount = db.FloatProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    decimals = db.IntegerProperty(required=False)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @property
    def tradeVolume_to_dict(self):
        if self.tradeVolume > 10000:
            return '%sk' %  math.floor(self.tradeVolume/1000)
        elif self.tradeVolume:
            return '%s' % self.tradeVolume
        else:
            return ''
