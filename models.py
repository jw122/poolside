import logging
from google.appengine.ext import db

class Token(db.Expando):
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
