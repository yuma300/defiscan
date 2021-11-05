import json
from kava_to_caaj.message import *
from kava_to_caaj.kava_util import *
from decimal import *
from datetime import datetime as dt
import logging
import re

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class Transaction:
  def __init__(self, transaction):
    self.transaction = transaction
    self.chain_id = transaction['header']['chain_id']
    self.fail = False
    self.time = dt.strptime(self.transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    if 'code' in transaction['data'] and transaction['data']['code'] != 0:
      logger.info(f'transaction: {transaction["data"]["txhash"]} is failed')
      self.fail = True
      return

  def get_transfers(self, recipient):
    transfers = list(filter(lambda x: x['type'] == 'transfer' and x['recipient'] == recipient, self.events))
    return transfers

  def get_fail(self):
    return self.fail
  
  def get_transaction_id(self):
    return self.transaction['data']['txhash'].lower()

  def get_time(self):
    return self.time.strftime('%Y-%m-%d %H:%M:%S')

  def get_fee(self):
    try:
      amount_list = self.transaction['data']['tx']['value']['fee']['amount']

      if amount_list != None and len(amount_list) > 0:
        amount = str(KavaUtil.convert_uamount_amount(amount_list[0]['amount']))
      else:
        amount = '0'
    except IndexError as e:
      logger.error("get_fee failed because cant found gas parameter\n transaction:")
      logger.error(json.dumps(self.transaction))
      raise e
    return amount