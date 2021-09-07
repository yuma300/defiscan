import requests
import time
import json
import sys


def main():
  address = sys.argv[1]
  #print(address)
  num_transactions = 50 
  last_id = 0
  f = open('transactions.txt', 'w')
  while num_transactions >= 50:
    time.sleep(5)
    response = requests.get(
        'https://api.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50})
    transactions = response.json()
    num_transactions = len(transactions) 
    #print(num_transactions)
    for transaction in transactions:
      last_id = transaction['header']['id']
      #print(last_id)
      f.write(json.dumps(transaction)+"\n")
      #print(transaction)
  f.close()

if __name__== '__main__':
    main()

