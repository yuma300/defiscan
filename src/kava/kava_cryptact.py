import requests
import time
import sys
import json
from decimal import Decimal
import pandas as pd
from scan import action
from datetime import datetime as dt
import re
import os
import logging
import re
from typing import Union
from pathlib import Path
from scan import kava8, kava9

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

Kava8B = kava8.Kava8B()
Kava9 = kava9.Kava9()

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

def read_config():
  f = open(".env.json","r")
  env_dict = json.load(f)
  return env_dict

def get_wallet_address():
  if "KAVA_WALLET_ADDRESS" in os.environ:
    return os.environ["KAVA_WALLET_ADDRESS"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["address"]
  else:
    return sys.argv[1].split(",")

# def split_amount(value:str)->tuple(int,str):
def split_amount(value:str)-> Union[Decimal, str]:
  amount = re.findall(r'\d+',value)[0]
  currency = re.findall(r'\D+',value)[0]
  logger.debug(f'split_amount : {amount} {currency}')
  currency_mapping = {
    'ukava':{'Name':'KAVA','precision':6},
    'hard':{'Name':'HARD','precision':6},
    'swp':{'Name':'SWP','precision':6},
    'busd':{'Name':'BUSD','precision':8},
    'usdx':{'Name':'USDX','precision':6},
  }
  amount = Decimal(amount) / Decimal(str(10**currency_mapping[currency]["precision"]))
  currency = currency_mapping[currency]["Name"]
  return amount,currency

def create_cryptact_csv(address):
  results = []
  transactions = []
  decoder = json.JSONDecoder()
  read_file_name = '%s/transactions_%s.txt' % (os.path.dirname(__file__), address)
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      line = json.loads(line)
      if "code" in line["data"] and line["data"]["code"] != 0:
        logger.debug(f"this transaction is error hash: {line['data']['txhash']}")
      else:
        transactions.append(line)
      line = f.readline()
  transactions.reverse()

  cdp_trucker = []
  #logger.debug(address)
  for transaction in transactions:
    #logger.debug(transaction)
    logger.debug(json.dumps(transaction['header'], indent=2))
    #logger.debug(json.dumps(transaction, indent=2))
    chain_id = transaction['header']['chain_id']
    timestamp = dt.strptime(transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    txhash = transaction['data']['txhash']
    fee = 0
    # before kava8
    if re.fullmatch(r"kava-[1-8]",chain_id):
      if(transaction['data']['tx']['type'] == "cosmos-sdk/StdTx"):
        try:
          fee = transaction['data']['tx']['value']['fee']['amount'][0]['amount']
          fee = Decimal(fee) / Decimal('1000000')
        except IndexError as e:
          logger.critical('this time has no fee.')

        #logger.debug(fee)
        if 'logs' in transaction['data']:
          results += Kava8B.cdp_tracking(cdp_trucker, transaction, fee, timestamp)
          logs = transaction['data']['logs']
          for log in logs:
            events = log['events']
            results += action.classify(timestamp, events, fee, txhash, address, chain_id)
        else:
          logger.debug(json.dumps(transaction['data']['raw_log']))
    # after kava9
    elif(transaction['data']['tx']['@type'] == "/cosmos.tx.v1beta1.Tx"):
      try:
        fee = transaction['data']['tx']['auth_info']['fee']['amount'][0]['amount']
        fee = Decimal(fee) / Decimal('1000000')
      except IndexError as e:
        logger.critical('this time has no fee.')

      #logger.debug(fee)
      if 'logs' in transaction['data']:
        results += Kava9.cdp_tracking(cdp_trucker, transaction, fee, timestamp)
        logs = transaction['data']['logs']
        for log in logs:
          events = log['events']
          results += action.classify(timestamp, events, fee, txhash, address, chain_id)
      else:
        logger.debug(json.dumps(transaction['data']['raw_log']))
  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  #logger.debug(df)
  result_file_name = 'kava_cryptact_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])


def main():
  addresses = get_wallet_address()
  for address in addresses:
    create_cryptact_csv(address)


if __name__== '__main__':
  set_root_logger()
  main()
