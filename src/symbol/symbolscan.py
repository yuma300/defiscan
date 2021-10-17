import requests
import logging
import json
import sys
import os
import time
from lib.SymbolExproler import SymbolExproler

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

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
  if "SYMBOL_WALLET_ADDRESS" in os.environ:
    return os.environ["SYMBOL_WALLET_ADDRESS"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["address"]
  else:
    return sys.argv[1].split(",")

def get_transactions(address,se=SymbolExproler()):
  file_name = f'harvests_{address}.txt'
  f = open(file_name, 'w')
  harvest_records = se.get_harvests(address)
  for harvest in harvest_records:
    f.write(json.dumps(harvest)+"\n")
    #logger.debug(transaction)
  f.close()

  file_name = f'transactions_{address}.txt'
  f = open(file_name, 'w')
  transactions_array = se.get_transactions(address)
  for transaction in transactions_array:
    f.write(json.dumps(transaction)+"\n")
    #logger.debug(transaction)
  f.close()



def main():
  addresses = get_wallet_address()
  logger.info(addresses)
  #logger.debug(address)
  for address in addresses:
    # logger.debug(address)
    get_transactions(address)
    # if you get dHealth Exproler, delete under comment.
    # get_transactions(address,se=SymbolExproler("http://dual-01.dhealth.cloud:3000"))

if __name__== '__main__':
  set_root_logger()
  main()