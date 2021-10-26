from decimal import *
import re
from typing import Union
import logging

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class KavaUtil:
  @classmethod
  def get_attribute_value(cls, attributes, key):
    return list(filter(lambda x: x['key'] == key, attributes))[0]['value']

  @classmethod
  def get_attribute_values(cls, attributes, key):
    attributes = list(filter(lambda x: x['key'] == key, attributes))
    return list(map(lambda x: x['value'], attributes))

  @classmethod
  def get_event_value(cls, events, type):
    event = list(filter(lambda x: x['type'] == type, events))
    if len(event) == 0:
      return None
    else:
      return event[0]

  @classmethod
  def get_event_values(cls, events, types:list):
    event = list(filter(lambda x: x['type'] in types, events))
    if len(event) == 0:
      return None
    else:
      return event

  @classmethod
  def convert_uamount_amount(cls, uamount, coin=None):
    denominator = 1000000
    if coin != None:
      if coin.lower() == 'busd':
        denominator = 100000000
      elif coin.lower() == 'bnb':
        denominator = 100000000
      elif coin.lower() == 'xrp':
        denominator = 100000000
    atom = Decimal(int(uamount)) / Decimal(denominator)
    return atom
  
  @classmethod
  def split_amount(cls, amount_coin:str)-> Union[Decimal, str]:
    amount = re.findall(r'\d+', amount_coin)[0]
    coin = amount_coin[len(amount):].upper()
    if coin == 'UKAVA':
      coin = 'KAVA'
    elif coin == 'XRPB':
      coin = 'XRP'
    return amount,coin