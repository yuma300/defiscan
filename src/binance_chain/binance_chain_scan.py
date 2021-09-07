import requests
import time
import json
import sys


def main():
  address = sys.argv[1]
  #print(address)
  page = 1
  MAX_NUM_TRANSACTIONS = 20
  num_transactions = 20
  f = open('transactions.txt', 'w')
  while num_transactions == MAX_NUM_TRANSACTIONS:
    time.sleep(5)
    response = requests.get(
        'https://api-binance-mainnet.cosmostation.io/v1/account/txs/%s' % address,
        params={'page': page, 'rows': MAX_NUM_TRANSACTIONS},
        headers={'Referrer Policy': 'strict-origin-when-cross-origin'})
    transactions = response.json()
    transactions = transactions['txArray']
    print(transactions)

    for transaction in transactions:
      f.write(json.dumps(transaction)+"\n")

    page += 1
    num_transactions = len(transactions) 
  f.close()

if __name__== '__main__':
    main()

