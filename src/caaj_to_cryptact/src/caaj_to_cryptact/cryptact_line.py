import logging
from decimal import *
from datetime import datetime as dt

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class CryptactLine:
  def __init__(self, line):
    self.timestamp = line['timestamp']
    self.action = line['action']
    self.source = line['source']
    self.base = line['base']
    self.volume = line['volume']
    self.price = line['price']
    self.counter = line['counter']
    self.fee = line['fee']
    self.feeccy = line['feeccy']
    self.comment = line['comment']
  
  def get_dict(self):
    line = {}
    line['timestamp'] = self.timestamp
    line['action'] = self.action   
    line['source'] = self.source   
    line['base']   = self.base   
    line['volume'] = self.volume   
    line['price'] = self.price   
    line['counter'] = self.counter   
    line['fee'] = self.fee   
    line['feeccy'] = self.feeccy   
    line['comment'] = self.comment   
    return line