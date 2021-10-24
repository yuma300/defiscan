import pandas as pd
from decimal import Decimal
from datetime import datetime as dt
import logging
import json
import sys
import os
from lib.SymbolExproler import SymbolExproler
from symbolchain.core.symbol.Network import Address
from binascii import unhexlify

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

# if use alt chain, change base name.
se = SymbolExproler()
base_currency_name = "XYM"
source_name = "Symbol"

# se = SymbolExproler("http://dual-01.dhealth.cloud:3000")
# base_currency_name = "DHC"
# source_name = "DHealthChain"

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
  harvests = []
  read_file_name = f'transactions_{address}.txt'
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      transactions.append(json.loads(line))
      line = f.readline()
  transactions.reverse()
  read_file_name = f'harvests_{address}.txt'
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      harvests.append(json.loads(line))
      line = f.readline()
  harvests.reverse()
  for transaction in transactions:
    results += transaction_classify(address,transaction)
  for harvest in harvests:
    results += harvest_classify(address,harvest)
  logger.debug(results)
  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  result_file_name = 'symbol_cryptact_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])


def is_own_transaction(address,transaction)->bool:
  own_public_key = se.get_account_public_key(address)
  transaction_public_key = transaction["transaction"]["signerPublicKey"]
  return transaction_public_key == own_public_key


def transaction_classify(address,transaction,length=1)->list[dict]:
  results = []
  # logger.debug(transaction)
  if "hash" in transaction["meta"]:
    transaction_hash = transaction["meta"]["hash"]
  elif "aggregateHash" in transaction["meta"]:
    transaction_hash = transaction["meta"]["aggregateHash"]
    aggregate = True
  transaction_block = transaction["meta"]["height"]
  if is_own_transaction(address,transaction):
    fee = se.fee_calculator(transaction_hash) # slowly
    fee = Decimal(fee) / Decimal(length)
  else:
    fee = 0
  timestamp = se.get_timestamp(transaction_block) # slowly
  # logger.debug(f"{transaction_public_key} {own_public_key}")
  url = f"http://explorer.symbolblockchain.io/transactions/{transaction_hash}"
  transaction_type = hex(transaction["transaction"]["type"])
  # logger.debug(transaction_type)
  # logger.debug(transaction_hash)
  # refference
  # https://docs.symbolplatform.com/concepts/transfer-transaction.html
  logger.info(f'{transaction_type} {transaction["transaction"]["type"]}')
  if transaction_type == "0x4154": # transfer 16724
    for mosaic in transaction["transaction"]["mosaics"]:
      amount = Decimal(mosaic["amount"]) / Decimal("1"+"0"*6)
      logger.debug(f"amount: {mosaic['amount']} {amount}")
      mosaicId = mosaic["id"]
      currency = se.get_symbol_names(mosaicId)
      if currency == "symbol.xym":
        currency = "XYM"
      recipient_address = Address(unhexlify(transaction["transaction"]["recipientAddress"]))
      logger.debug(f"{recipient_address} {address}")
      if str(recipient_address) == address: # reciver
        results.append({'Timestamp': timestamp, 'Source': source_name, 'Action': 'BONUS', 'Base': base_currency_name, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': base_currency_name, 'Comment': f'recive {url}'})
        pass
      if is_own_transaction(address,transaction): # sender
        results.append({'Timestamp': timestamp, 'Source': source_name, 'Action': 'SENDFEE', 'Base': base_currency_name, 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': base_currency_name, 'Comment': f'send {url}'})
  elif transaction_type == "0x4141": # aggregate transaction 16705
    aggreagte_transactions = se.get_aggregate_transactions(transaction_hash)
    transactions_length = len(aggreagte_transactions) # use fee calc
    send_transactions = list(filter(lambda transaction: "0x4154" == hex(transaction["transaction"]["type"]),aggreagte_transactions))
    aggreagte_send_transactionslist = (filter(lambda transaction: address == str(Address(unhexlify(transaction["transaction"]["recipientAddress"]))),send_transactions))
    for aggreagte_transaction in aggreagte_send_transactionslist:
      results += transaction_classify(address,aggreagte_transaction,length=transactions_length) #retrative classify
  else:
    if is_own_transaction(address,transaction):
      if fee > 0:
        logger.info(f"no hit transaction: {transaction_type}")
        results.append({'Timestamp': timestamp, 'Source': source_name, 'Action': 'SENDFEE', 'Base': base_currency_name, 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': base_currency_name, 'Comment':f' common {url}'})
  return results


def harvest_classify(address,harvest)->list[dict]:
  # logger.debug(transaction)
  transaction_block = harvest["statement"]["height"]
  timestamp = se.get_timestamp(transaction_block)
  url = f"http://explorer.symbolblockchain.io/blocks/{transaction_block}"
  for receipts in harvest["statement"]["receipts"]:
    if "targetAddress" in receipts:
      target_address = Address(unhexlify(receipts["targetAddress"]))
      if str(target_address) == address:
        # print(receipts["amount"])
        amount = Decimal(receipts["amount"]) / Decimal("1"+"0"*6)
        result = {'Timestamp': timestamp, 'Source': source_name, 'Action': 'STAKING', 'Base': base_currency_name, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': base_currency_name, 'Comment': f'{url}'}
        return [result]
        # logger.debug(f"{target_address}: {receipts['amount']}")
        # harvest_array.append(harvest)

  # transaction_type = hex(harvest["transaction"]["type"])


def main():
  addresses = get_wallet_address()
  for address in addresses:
    create_cryptact_csv(address)


if __name__ == "__main__":
  set_root_logger()
  main()