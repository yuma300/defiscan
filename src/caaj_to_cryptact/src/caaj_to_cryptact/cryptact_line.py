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
    line['Timestamp'] = self.timestamp
    line['Action'] = self.action   
    line['Source'] = self.source   
    line['Base']   = self.base   
    line['Volume'] = self.volume   
    line['Price'] = self.price   
    line['Counter'] = self.counter   
    line['Fee'] = self.fee   
    line['FeeCcy'] = self.feeccy   
    line['Comment'] = self.comment   
    return line