import requests
import time
import json
import sys
import os
import logging

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.DEBUG)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.DEBUG)
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

def get_transactions(address):
  num_transactions = 50
  last_id = 0
  file_name = 'transactions_%s.txt' % address
  f = open(file_name, 'w')
  while num_transactions >= 50:
    time.sleep(5)
    headers = {
        "Origin": "https://www.mintscan.io",
        "Referer": "https://www.mintscan.io/",
    }  # workaround from 2022-04-25: both origin and referer headers are required
    response = requests.get(
        'https://api-kava.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50}, headers=headers)
    transactions = response.json()
    num_transactions = len(transactions)
    #print(num_transactions)
    for transaction in transactions:
      last_id = transaction['header']['id']
      #print(last_id)
      f.write(json.dumps(transaction)+"\n")
      #print(transaction)
  f.close()

def main():
  addresses = get_wallet_address()
  logger.info(addresses)
  #print(address)
  for address in addresses:
    # print(address)
    get_transactions(address)


if __name__== '__main__':
  set_root_logger()
  main()

