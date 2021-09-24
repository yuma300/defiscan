import pandas as pd
from decimal import Decimal
from datetime import datetime as dt
import logging
import json
import sys
import os

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

def create_cryptact_csv(address):
  results = []
  transactions = []
  payments = []
  decoder = json.JSONDecoder()
  read_file_name = f'transactions_{address}.txt'
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      transactions.append(json.loads(line))
      line = f.readline()
  transactions.reverse()
  read_file_name = f'payments_{address}.txt'
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      payments.append(json.loads(line))
      line = f.readline()
  payments.reverse()

  for transaction in transactions:
    if transaction["successful"] is not True:
      logger.info(f"this transaction is not successful. id:{id}")
      continue
    if transaction["fee_account"] == address:
      fee = Decimal(transaction["fee_charged"])/Decimal("10000000")
      timestamp = dt.strptime(transaction['created_at'], '%Y-%m-%dT%H:%M:%SZ')
      url = f"https://stellar.expert/explorer/public/tx/{transaction['id']}"
      results.append({'Timestamp': timestamp, 'Source': 'stellar','Action': 'SENDFEE', 'Base': 'XLM', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'XLM', 'Comment': f'send fee {url}'})
  for payment in payments:
    if payment["transaction_successful"] is not True:
      logger.info(f"this payment is not successful. id:{id}")
      continue
    if payment["asset_type"] == "native":
      base = "XLM"
    else:
      base = payment["asset_code"]
    if payment["type"] == "payment":
      # Keybase Space Drop
      # https://www.coindesk.com/markets/2019/09/09/stellar-to-give-away-2-billion-xlm-valued-at-120-million-today/
      if payment["source_account"] == "GDV4KECLSZLKRVH4ZTWVAS4I3W2LPAPV66ADFFUZKGIVOTK6GMKGJT53":
        timestamp = dt.strptime(transaction['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        url = f"https://stellar.expert/explorer/public/tx/{transaction['id']}"
        results.append({'Timestamp': timestamp, 'Source': 'stellar','Action': 'BONUS', 'Base': base, 'Volume': payment["amount"], 'Price': 0, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'XLM', 'Comment': f'AirDrop {url}'})

  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  result_file_name = 'stellar_cryptact_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])

def main():
  addresses = get_wallet_address()
  logger.info(addresses)
  #print(address)
  for address in addresses:
    # print(address)
    create_cryptact_csv(address)


if __name__== '__main__':
  set_root_logger()
  main()
