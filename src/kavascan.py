import requests
import time
import sys


def main():
  address = sys.argv[1]
  #print(address)
  num_transactions = 50 
  last_id = 0
  while num_transactions >= 50:
    time.sleep(5)
    response = requests.get(
        'https://api-kava.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50})
    transactions = response.json()
    num_transactions = len(transactions) 
    #print(num_transactions)
    for transaction in transactions:
      last_id = transaction['header']['id']
      #print(last_id)
      print(transaction)


if __name__== '__main__':
    main()

