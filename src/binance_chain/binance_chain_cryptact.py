import requests
import time
import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt
import re


def main():
  address = sys.argv[1]    
  results = []
  transactions = []
  decoder = json.JSONDecoder()
  with open('transactions.txt', 'r') as f:
    line = f.readline()
    while line:
      transactions.append(json.loads(line))
      line = f.readline()
  transactions.reverse()

  print(address)
  for transaction in transactions:
    print(transaction)
    results += classify(transaction, address)

  #print(results)
  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  print(df)
  df.to_csv('binance_chain_cryptact.csv', index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])

def classify(transaction, address):
  txType = transaction['txType']
  results = []
  timestamp = int(int(transaction['timeStamp'])/1000)
  timestamp = dt.fromtimestamp(timestamp)
  txhash = transaction['txHash']
  fromAddr = transaction['fromAddr']
  txFee =  transaction['txFee']
  print(fromAddr)

  if fromAddr != address:
    return results

  if txType in ['HTL_TRANSFER', 'TRANSFER', 'SIDECHAIN_DELEGATE', 'CLAIM_HTL']:
    results.append({'Timestamp': timestamp, 'Source': 'binance_chain', 'Action': 'SENDFEE', 'Base': 'BNB', 'Volume': txFee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'BNB', 'Comment': '%s https://www.mintscan.io/kava/txs/%s' % (txType, txhash)})
  else:
    raise ValueError('%s: this is undefined action ...' % txType)
  
  return results


if __name__== '__main__':
    main()

