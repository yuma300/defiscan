from decimal import *
import re
from typing import Union
import logging
from src.caaj_to_cryptact import *
from src.caaj_to_cryptact.caaj_line import *
from src.caaj_to_cryptact.cryptact_line import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 12

class CaajToCryptact:
  @classmethod
  def convert(cls, caajline:CaajLine):
    cryptact_line = None
    if caajline.debit_title == 'FEE' and caajline.credit_title == 'SPOT':
      cryptact_line = cls.fee(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'STAKINGREWARD':
      cryptact_line = cls.staking_reward(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'LENDINGREWARD':
      cryptact_line = cls.lending_reward(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'SPOT':
      cryptact_line = cls.swap(caajline)
    return cryptact_line
  
  def fee(caajline:CaajLine):
    base = list(caajline.debit_amount.keys())[0]
    volume = list(caajline.debit_amount.values())[0]

    cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'SENDFEE', 'source':caajline.platform, 
      'base':base, 'volume':volume, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return cryptact_line

  def staking_reward(caajline:CaajLine):
    for key, value in caajline.debit_amount.items():
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'STAKING', 'source':caajline.platform, 
        'base':key, 'volume':value, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return cryptact_line

  def lending_reward(caajline:CaajLine):
    for key, value in caajline.debit_amount.items():
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'LENDING', 'source':caajline.platform, 
        'base':key, 'volume':value, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return cryptact_line

  def swap(caajline:CaajLine):
    buy_token = list(caajline.debit_amount.keys())[0]
    buy_amount = list(caajline.debit_amount.values())[0]

    sell_token = list(caajline.credit_amount.keys())[0]
    sell_amount = list(caajline.credit_amount.values())[0]

    cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'BUY', 'source':caajline.platform, 
      'base':buy_token, 'volume':buy_amount, 'price':str(Decimal(buy_amount)/Decimal(sell_amount)), 'counter':sell_token, 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})

    return cryptact_line