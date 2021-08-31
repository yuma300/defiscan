import requests
import time
import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt
import re

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

def cdp_tracking(cdp_trucker, transaction, fee, timestamp):
  results = []
  tx_msg = transaction['data']['tx']['value']['msg'][0]
  action = tx_msg['type']
  txhash = transaction['data']['txhash']
  if action == 'cdp/MsgCreateCDP':
    collateral_token = tx_msg['value']['collateral_type']
    cdp_list = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))
    if len(cdp_list) > 0: # check same collateral cdp already exist. if true, it means liquidation was executed.
      cdp = cdp_list[0]
      results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': cdp['debt_amount'], 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp liquidated https://www.mintscan.io/kava/txs/%s' % txhash})
      cdp_trucker.remove(cdp)
      
    collateral_amount = Decimal(tx_msg['value']['collateral']['amount']) / Decimal('100000000')
    debt_amount = Decimal(tx_msg['value']['principal']['amount'])/ Decimal('1000000')
    cdp = {'collateral_token': collateral_token, 'collateral_amount': collateral_amount, 'debt_amount': debt_amount}
    cdp_trucker.append(cdp)
    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'BORROW', 'Base': 'USDX', 'Volume': debt_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp create https://www.mintscan.io/kava/txs/%s' % txhash})
  elif action == 'cdp/MsgDrawDebt':
    collateral_token = tx_msg['value']['collateral_type']
    debt_amount = Decimal(tx_msg['value']['principal']['amount'])/ Decimal('1000000')
    try:
      cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
      cdp['debt_amount'] += debt_amount
    except IndexError as e:
      print('cdp/MsgDrawDebt. CDP does not exist!!!!!!')
      raise e

    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'BORROW', 'Base': 'USDX', 'Volume': debt_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp draw https://www.mintscan.io/kava/txs/%s' % txhash})
  elif action == 'cdp/MsgRepayDebt':
    events = transaction['data']['logs'][0]['events']
    collateral_token = tx_msg['value']['collateral_type']
    repay_amount = Decimal(tx_msg['value']['payment']['amount'])/ Decimal('1000000')
    try:
      cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
      if len(list(filter(lambda item: item['type'] == 'cdp_close', events))) != 0: # check wether close or not
        if cdp['debt_amount'] - repay_amount > 0: # check total debt amount is not bigger than total repayamount
          raise ValueError('%s: total debt amount (%s) is bigger than total repayment (%s).' % (collateral_token, cdp['debt_amount'], repay_amount))
        interest_amount = repay_amount - cdp['debt_amount'] # calcurate interest amount
        transfer_attributes = list(filter(lambda item: item['type'] == 'transfer', events))[0]['attributes']
        withdraw_amount = list(filter(lambda item: item['key'] == 'amount' and 'usdx' not in item['value'], transfer_attributes))[0]['value']
        withdraw_amount = Decimal(re.sub(r"\D", "", withdraw_amount))/ Decimal('100000000')

        if cdp['collateral_amount'] != withdraw_amount: # check withdraw amount is equal to collateral_amount
          raise ValueError('%s: collateral_amount is not equal to withdraw amount (%s)' % collateral_token, cdp['collateral_amount'], withdraw_amount)

        results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': cdp['debt_amount'], 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp close https://www.mintscan.io/kava/txs/%s' % txhash})
        results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SELL', 'Base': 'USDX', 'Volume': interest_amount, 'Price': 0, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'cdp repay interest https://www.mintscan.io/kava/txs/%s' % txhash})
        cdp_trucker.remove(cdp)
      else:
        if cdp['debt_amount'] - repay_amount < 0: # check total debt amount is bigger than total repayamount
          raise ValueError('%s: total debt amount is not bigger than total repayment.' % collateral_token)
        cdp['debt_amount'] -= repay_amount
        results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': repay_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp repay https://www.mintscan.io/kava/txs/%s' % txhash})
    except IndexError as e:
      print('cdp/MsgRepayDebt. CDP does not exist!!!!!!')
      raise e
  elif action == 'cdp/MsgWithdraw':
    collateral_token = tx_msg['value']['collateral_type']
    collateral_amount = Decimal(tx_msg['value']['collateral']['amount'])/ Decimal('100000000')
    try:
      cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
      if cdp['collateral_amount'] - Decimal(collateral_amount) < 0: # check total withdraw amount is not bigger than collateral
        raise ValueError('%s: withdraw amount (%s) is bigger than collateral amount (%s).' % collateral_token, collateral_amount, cdp['collateral_amount'])
      cdp['collateral_amount'] -= Decimal(collateral_amount)
    except IndexError as e:
      print('cdp/MsgWithdraw. CDP does not exist!!!!!!')
      raise e

    if fee == 0: return results 
    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp https://www.mintscan.io/kava/txs/%s' % txhash})
  elif action == 'cdp/MsgDeposit':
    collateral_token = tx_msg['value']['collateral_type']
    collateral_amount = Decimal(tx_msg['value']['collateral']['amount'])/ Decimal('100000000')
    try:
      cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
      cdp['collateral_amount'] += Decimal(collateral_amount)
    except IndexError as e:
      print('cdp/MsgDeposit. CDP does not exist!!!!!!')
      raise e

    if fee == 0: return results 
    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp https://www.mintscan.io/kava/txs/%s' % txhash})

  #print(cdp_trucker)
  return results

      

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

  cdp_trucker = []
  #print(address)
  for transaction in transactions:
    #transaction = json.loads(transaction)
    #print(transaction)
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

    #print(fee)
    if 'logs' in transaction['data']:
      results += cdp_tracking(cdp_trucker, transaction, fee, timestamp)
      logs = transaction['data']['logs']
      for log in logs:
        events = log['events']
        results += classify(timestamp, events, fee, txhash, address)
    else:
      print(json.dumps(transaction['data']['raw_log']))

  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  #print(df)
  df.to_csv('kava_cryptact.csv', index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])


def classify(timestamp, events, fee, txhash, address):
  results = []
  #print(json.dumps(events, indent=2))
  message = list(filter(lambda item: item['type'] == 'message', events))[0]
  action = list(filter(lambda item: item['key'] == 'action', message['attributes']))[0]['value']
  #print(events)
  if action == 'create_cdp':
    print('create_cdp')
  elif action == 'draw_cdp':
    print('draw_cdp')
  elif action == 'deposit_cdp':
    print('deposit_cdp')
  elif action == 'repay_cdp':
    print('repay_cdp')
  elif action == 'withdraw_cdp':
    print('withdraw_cdp')
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
  #print(results)
  return results



if __name__== '__main__':
    main()

