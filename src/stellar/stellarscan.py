from stellar_sdk import Server
# https://github.com/StellarCN/py-stellar-base/blob/master/examples/query_horizon.py
import requests
import logging
import json
import sys
import os

# ------------------
# This script is *not* adapt airdrop
# ------------------

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
  if "STELLAR_WALLET_ADDRESS" in os.environ:
    return os.environ["STELLAR_WALLET_ADDRESS"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["address"]
  else:
    return sys.argv[1].split(",")

def get_transactions(address):
    server = Server(horizon_url="https://horizon.stellar.org")
    file_name = f'transactions_{address}.txt'
    f = open(file_name, 'w')
    transactions_records = []
    transactions_call_builder = (
        server.transactions().for_account(account_id=address).order(desc=False).limit(10)
    )
    transactions_records += transactions_call_builder.call()["_embedded"]["records"]
    page_count = 0
    while page_records := transactions_call_builder.next()["_embedded"]["records"]:
        transactions_records += page_records
        logger.debug(f"Page {page_count} fetched")
        logger.debug(f"data: {page_records}")
        page_count += 1
    logger.debug(f"transactions count: {len(transactions_records)}")
    logger.debug(transactions_records)
    for transaction in transactions_records:
      f.write(json.dumps(transaction)+"\n")
      #logger.debug(transaction)
    f.close()

    file_name = f'payments_{address}.txt'
    f = open(file_name, 'w')
    server = Server(horizon_url="https://horizon.stellar.org")
    payments_records = []
    payments_call_builder = (
        server.payments().for_account(account_id=address).order(desc=False).limit(10)
    )
    payments_records += payments_call_builder.call()["_embedded"]["records"]
    page_count = 0
    while page_records := payments_call_builder.next()["_embedded"]["records"]:
        payments_records += page_records
        logger.debug(f"Page {page_count} fetched")
        logger.debug(f"data: {page_records}")
        page_count += 1
    logger.debug(f"payments count: {len(payments_records)}")
    for transaction in payments_records:
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


if __name__== '__main__':
  set_root_logger()
  main()

