from decimal import *
import re
from typing import Union
import logging
from caaj_to_cryptact import *
from caaj_to_cryptact.caaj_line import *
from caaj_to_cryptact.cryptact_line import *
from caaj_to_cryptact.balance_cache import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class CaajToCryptact:
  @classmethod
  def convert(cls, caajline:CaajLine):
    cryptact_lines = None
    if caajline.debit_title == 'FEE' and caajline.credit_title == 'SPOT':
      cryptact_lines = cls.fee(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'RECEIVE':
      pass
    elif caajline.debit_title == 'SEND' and caajline.credit_title == 'SPOT':
      pass
    elif caajline.debit_title == 'STAKING' and caajline.credit_title == 'SPOT':
      pass
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'STAKING':
      pass
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'STAKINGREWARD':
      cryptact_lines = cls.staking_reward(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'LENDINGREWARD':
      cryptact_lines = cls.lending_reward(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'SPOT':
      cryptact_lines = cls.swap(caajline)
    elif caajline.debit_title == 'LEND' and caajline.credit_title == 'SPOT':
      cryptact_lines = cls.lend(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'LEND':
      cryptact_lines = cls.withdraw(caajline)
    elif caajline.debit_title == 'SPOT' and caajline.credit_title == 'BORROW':
      cryptact_lines = cls.borrow(caajline)
    elif caajline.debit_title == 'BORROW' and caajline.credit_title == 'SPOT':
      cryptact_lines = cls.repay(caajline)
    else:
      raise ValueError(f"Undefined title combination. debit_title:{caajline.debit_title} credit_title:{caajline.credit_title}")
    return cryptact_lines
  
  def lend(caajline:CaajLine):
    token = list(caajline.debit_amount.keys())[0]
    amount = list(caajline.debit_amount.values())[0]
    BalanceCache.add(caajline.platform, 'lend', token, amount)

  def withdraw(caajline:CaajLine):
    token = list(caajline.credit_amount.keys())[0]
    amount = Decimal(list(caajline.credit_amount.values())[0])
    current_lend_amount = Decimal(BalanceCache.get(caajline.platform, 'lend', token))
    cryptact_lines = []
    if current_lend_amount < amount:
      if current_lend_amount > 0:
        BalanceCache.set(caajline.platform, 'lend', token, '0')
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'LENDING', 'source':caajline.platform, 
        'base':token, 'volume':str(amount - current_lend_amount), 'price':'0', 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
      cryptact_lines.append(cryptact_line)
    else:
      BalanceCache.sub(caajline.platform, 'lend', token, amount)      

    return cryptact_lines

  def borrow(caajline:CaajLine):
    token = list(caajline.debit_amount.keys())[0]
    amount = list(caajline.debit_amount.values())[0]
    BalanceCache.add(caajline.platform, 'borrow', token, amount)

    cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'BORROW', 'source':caajline.platform, 
      'base':token, 'volume':amount, 'price': None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return [cryptact_line]

  def repay(caajline:CaajLine):
    token = list(caajline.credit_amount.keys())[0]
    amount = Decimal(list(caajline.credit_amount.values())[0])
    current_borrow_amount = Decimal(BalanceCache.get(caajline.platform, 'borrow', token))
    cryptact_lines = []
    if current_borrow_amount < amount:
      if current_borrow_amount > 0:
        BalanceCache.set(caajline.platform, 'borrow', token, '0')
        cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'RETURN', 'source':caajline.platform, 
          'base':token, 'volume':str(current_borrow_amount), 'price':'0', 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
        cryptact_lines.append(cryptact_line)
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'SELL', 'source':caajline.platform, 
        'base':token, 'volume':str(amount - current_borrow_amount), 'price':'0', 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
      cryptact_lines.append(cryptact_line)
    else:
      BalanceCache.sub(caajline.platform, 'borrow', token, amount)
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'RETURN', 'source':caajline.platform, 
        'base':token, 'volume':str(amount), 'price':'0', 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
      cryptact_lines.append(cryptact_line)

    return cryptact_lines


  def fee(caajline:CaajLine):
    base = list(caajline.debit_amount.keys())[0]
    volume = list(caajline.debit_amount.values())[0]

    cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'SENDFEE', 'source':caajline.platform, 
      'base':base, 'volume':volume, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return [cryptact_line]

  def staking_reward(caajline:CaajLine):
    for key, value in caajline.debit_amount.items():
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'STAKING', 'source':caajline.platform, 
        'base':key, 'volume':value, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return [cryptact_line]

  def lending_reward(caajline:CaajLine):
    for key, value in caajline.debit_amount.items():
      cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'LENDING', 'source':caajline.platform, 
        'base':key, 'volume':value, 'price':None, 'counter':'JPY', 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})
    return [cryptact_line]

  def swap(caajline:CaajLine):
    buy_token = list(caajline.debit_amount.keys())[0]
    buy_amount = list(caajline.debit_amount.values())[0]

    sell_token = list(caajline.credit_amount.keys())[0]
    sell_amount = list(caajline.credit_amount.values())[0]

    cryptact_line = CryptactLine({'timestamp':caajline.time, 'action':'BUY', 'source':caajline.platform, 
      'base':buy_token, 'volume':buy_amount, 'price':str(Decimal(buy_amount)/Decimal(sell_amount)), 'counter':sell_token, 'fee':'0', 'feeccy':'JPY', 'comment':caajline.comment})

    return [cryptact_line]