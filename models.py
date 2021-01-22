import logging
from google.appengine.ext import db


class Model():
    def to_dict(self):
       return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

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

class Pair(db.Expando, Model):
    # key_name is id
    id = db.StringProperty()
    symbol = db.StringProperty(required=False)
    name = db.StringProperty(required=False)
    tradeVolume = db.FloatProperty(required=False)
    tradeCount = db.FloatProperty(required=False)
    created = db.DateTimeProperty(required=False)
    modified = db.DateTimeProperty(auto_now=True)