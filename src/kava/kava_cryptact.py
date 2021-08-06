import requests
import time
import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt

# types on mintscan web      : types on mintscan api
# CDP Draw Debt              : draw_cdp
# CDP Deposit                : deposit_cdp
# CDP Repay Debt             : repay_cdp
# CDP Withdraw               : withdraw_cdp
# Claim Atomic Swap          : claimAtomicSwap
# Claim HARD LP Reward       : claim_hard_reward
# Claim USDX Minting Reward  : claim_usdx_minting_reward
# Create Atomic Swap         : createAtomicSwap
# Create CDP                 : create_cdp
# Delegate                   : delegate
# Get Reward                 : withdraw_delegator_reward 
# HARD Deposit               : hard_deposit
# HARD Withdraw              : hard_withdraw
# Harvest Claim Reward       : claim_harvest_reward
# Harvest Deposit            : harvest_deposit
# Harvest Withdraw           : harvest_withdraw
# MsgClaimReward             : claim_reward
# Refund Atomic Swap         : refundAtomicSwap
# Send                       : send
# Undelegate                 : begin_unbonding
# Vote                       : vote

def main():
  address = sys.argv[1]
  #print(address)
  num_transactions = 50 
  last_id = 0
  results = []
  while num_transactions >= 50:
    time.sleep(3)
    response = requests.get(
        'https://api-kava.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': last_id, 'limit': 50})
    transactions = response.json()
    num_transactions = len(transactions) 
    #print(num_transactions)
    for transaction in transactions:
      last_id = transaction['header']['id']
      #print(last_id)
      print(json.dumps(transaction['header'], indent=2))
      #print(json.dumps(transaction, indent=2))
      timestamp = dt.strptime(transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ') 
      txhash = transaction['data']['txhash']
      fee = 0
      try:
        fee = transaction['data']['tx']['value']['fee']['amount'][0]['amount']
        fee = Decimal(fee) / Decimal('1000000')
      except IndexError as e:
        print('this time has no fee.')

      print(fee)
      if 'logs' in transaction['data']:
        logs = transaction['data']['logs']
        for log in logs:
          events = log['events']
          results = results + classify(timestamp, events, fee, txhash, address)
      else:
        print(json.dumps(transaction['data']['raw_log']))

  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  print(df)
  df.to_csv('kava_cryptact.csv', index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])


def classify(timestamp, events, fee, txhash, address):
  results = []
  #print(json.dumps(events, indent=2))
  message = list(filter(lambda item: item['type'] == 'message', events))[0]
  action = list(filter(lambda item: item['key'] == 'action', message['attributes']))[0]['value']
  #print(events)
  if action == 'create_cdp':
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount' and 'usdx' in item['value'], transfer['attributes']))[0]['value']
    amount = Decimal(amount.replace('usdx', '')) / Decimal('1000000')
    results.append({'Action': 'BORROW', 'Base': 'USDX', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp create'})
  elif action == 'draw_cdp':
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = Decimal(amount.replace('usdx', '')) / Decimal('1000000')
    results.append({'Action': 'BORROW', 'Base': 'USDX', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp draw debt'})
  elif action == 'deposit_cdp':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp'})
  elif action == 'repay_cdp':
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = Decimal(amount.replace('usdx', '')) / Decimal('1000000')
    results.append({'Action': 'RETURN', 'Base': 'USDX', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp repay debt'})
  elif action == 'withdraw_cdp':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'withdraw cdp'})
  elif action == 'claimAtomicSwap':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  elif action in ['claim_hard_reward', 'claim_harvest_reward']:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    hard_amount = list(filter(lambda item: 'hard' in item, amount.split(',')))[0]
    hard_amount = Decimal(hard_amount.replace('hard', '')) / Decimal('1000000')
    results.append({'Action': 'LENDING', 'Base': 'HARD', 'Volume': hard_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim HARD of hard lending reward'})

    try:
      kava_amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
      kava_amount = Decimal(kava_amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'LENDING', 'Base': 'KAVA', 'Volume': kava_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim KAVA of hard lending reward'})
    except IndexError as e:
      print('no KAVA reward on hard')

  elif action in ['claim_usdx_minting_reward', 'claim_reward']:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
    results.append({'Action': 'LENDING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim kava usdx minting reward'})
  elif action == 'createAtomicSwap':
    if fee == 0: return results 
    message_attributes = list(filter(lambda item: item['type'] == 'message', events))[0]['attributes']
    sender = list(filter(lambda item: item['key'] == 'sender', message_attributes))[0]['value']
    if sender != address: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  elif action in ['delegate','withdraw_delegator_reward']:
    try:
      transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
      amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
      amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
    except IndexError as e:
      print('this time. no auto claim reward.')
  elif action in ['hard_deposit', 'harvest_deposit']:
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard deposit'})
  elif action in ['hard_withdraw', 'harvest_withdraw']:
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard withdraw'})
  elif action == 'refundAtomicSwap':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'refund atomic swap'})
  elif action == 'send':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'send'})
  elif action == 'begin_unbonding':
    try:
      transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
      amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
      amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
    except IndexError as e:
      print('this time. no auto claim reward.')
  elif action == 'vote':
    if fee == 0: return results 
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'vote'})
  else:
    raise ValueError('%s: this is undefined action ...' % action)

  results = list(map(lambda item: item|{'Timestamp': timestamp, 'Source': 'kava', 'Comment': item['Comment'] + ' https://www.mintscan.io/kava/txs/%s' % txhash}, results))
  print(results)
  return results



if __name__== '__main__':
    main()

