import requests
import time
import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt
import re
import os
import logging
import re
from typing import Union
from pathlib import Path

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

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
# HARD Withdraw              : hard_borrow
# HARD Repay                 : hard_repay
# Deposit                    : swap_deposit
# Withdraw                   : swap_withdraw
# Claim Swap Reward          : claim_swap_reward
# Comitty Vote               : committee_vote

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
  if "KAVA_WALLET_ADDRESS" in os.environ:
    return os.environ["KAVA_WALLET_ADDRESS"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["address"]
  else:
    return sys.argv[1].split(",")

# def split_amount(value:str)->tuple(int,str):
def split_amount(value:str)-> Union[Decimal, str]:
  amount = re.findall(r'\d+',value)[0]
  currency = re.findall(r'\D+',value)[0]
  logger.debug(f'split_amount : {amount} {currency}')
  currency_mapping = {
    'ukava':{'Name':'KAVA','precision':6},
    'hard':{'Name':'HARD','precision':6},
    'swp':{'Name':'SWP','precision':6},
    'busd':{'Name':'BUSD','precision':8},
    'usdx':{'Name':'USDX','precision':6},
  }
  amount = Decimal(amount) / Decimal(str(10**currency_mapping[currency]["precision"]))
  currency = currency_mapping[currency]["Name"]
  return amount,currency

def cdp_tracking(cdp_trucker, transaction, fee, timestamp):
  results = []
  chain_id = transaction['header']['chain_id']
  if chain_id == 'kava-9':
    tx_msg = transaction['data']['tx']['body']['messages'][0]
    action = tx_msg['@type']
  else:
    tx_msg = transaction['data']['tx']['value']['msg'][0]
    action = tx_msg['type']
  txhash = transaction['data']['txhash']
  events = transaction['data']['logs'][0]['events']
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
      logger.critical('cdp/MsgDrawDebt. CDP does not exist!!!!!!')
      raise e

    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'BORROW', 'Base': 'USDX', 'Volume': debt_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp draw https://www.mintscan.io/kava/txs/%s' % txhash})
  elif action in ['cdp/MsgRepayDebt', '/kava.cdp.v1beta1.MsgRepayDebt']:
    if chain_id == 'kava-9':
      collateral_token = tx_msg['collateral_type']
      repay_amount = Decimal(tx_msg['payment']['amount'])/ Decimal('1000000')
    else:
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
      logger.critical('cdp/MsgRepayDebt. CDP does not exist!!!!!!')
      raise e
  elif action in ['cdp/MsgWithdraw', '/kava.cdp.v1beta1.MsgWithdraw']:
    if chain_id == 'kava-9':
      collateral_token = tx_msg['collateral_type']
      collateral_amount = Decimal(tx_msg['collateral']['amount'])/ Decimal('100000000')
    else:
      collateral_token = tx_msg['value']['collateral_type']
      collateral_amount = Decimal(tx_msg['value']['collateral']['amount'])/ Decimal('100000000')
    try:
      cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
      if cdp['collateral_amount'] - Decimal(collateral_amount) < 0: # check total withdraw amount is not bigger than collateral
        raise ValueError('%s: withdraw amount (%s) is bigger than collateral amount (%s).' % collateral_token, collateral_amount, cdp['collateral_amount'])
      cdp['collateral_amount'] -= Decimal(collateral_amount)
    except IndexError as e:
      logger.critical('cdp/MsgWithdraw. CDP does not exist!!!!!!')
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
      logger.critical('cdp/MsgDeposit. CDP does not exist!!!!!!')
      raise e

    if fee == 0: return results
    results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp https://www.mintscan.io/kava/txs/%s' % txhash})
  elif action == 'swap/MsgSwapExactForTokens':
    pass
    # input_denominator = Decimal('1000000') if tx_msg['value']['exact_token_a']['denom'] != 'busd' else Decimal('100000000')
    # input_token = tx_msg['value']['exact_token_a']['denom'].upper()
    # input_amount = Decimal(tx_msg['value']['exact_token_a']['amount'])/ input_denominator
    # output_denominator = Decimal('1000000') if tx_msg['value']['token_b']['denom'] != 'busd' else Decimal('100000000')
    # output_token = tx_msg['value']['token_b']['denom'].upper()
    # output_amount = Decimal(tx_msg['value']['token_b']['amount'])/ output_denominator
    # price = output_amount / input_amount
    # results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SELL', 'Base': input_token, 'Volume': input_amount, 'Price': price, 'Counter': output_token, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'swap https://www.mintscan.io/kava/txs/%s' % txhash})

  #print(cdp_trucker)
  return results


def create_cryptact_csv(address):
  results = []
  transactions = []
  decoder = json.JSONDecoder()
  read_file_name = '%s/transactions_%s.txt' % (os.path.dirname(__file__), address)
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      transactions.append(json.loads(line))
      line = f.readline()
  transactions.reverse()

  cdp_trucker = []
  #logger.debug(address)
  for transaction in transactions:
    #transaction = json.loads(transaction)
    #logger.debug(transaction)
    logger.debug(json.dumps(transaction['header'], indent=2))
    #logger.debug(json.dumps(transaction, indent=2))
    chain_id = transaction['header']['chain_id']
    timestamp = dt.strptime(transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    txhash = transaction['data']['txhash']
    fee = 0
    try:
      if chain_id == 'kava-9':
        fee = transaction['data']['tx']['auth_info']['fee']['amount'][0]['amount']
      else:
        fee = transaction['data']['tx']['value']['fee']['amount'][0]['amount']
      fee = Decimal(fee) / Decimal('1000000')
    except IndexError as e:
      logger.critical('this time has no fee.')

    #logger.debug(fee)
    if 'logs' in transaction['data']:
      results += cdp_tracking(cdp_trucker, transaction, fee, timestamp)
      logs = transaction['data']['logs']
      for log in logs:
        events = log['events']
        results += classify(timestamp, events, fee, txhash, address, chain_id)
    else:
      logger.debug(json.dumps(transaction['data']['raw_log']))

  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  #logger.debug(df)
  result_file_name = 'kava_cryptact_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])

swp_lp_amount = {} # for reqidity provide calc variable
hard_rending_amount = {} # for rending deposit calc variable
def classify(timestamp, events, fee, txhash, address, chain_id):
  results = []
  global swp_lp_amount
  global hard_rending_amount
  #logger.debug(json.dumps(events, indent=2))
  message = list(filter(lambda item: item['type'] == 'message', events))[0]
  action = list(filter(lambda item: item['key'] == 'action', message['attributes']))[0]['value']
  #logger.debug(events)
  if action == 'create_cdp':
    logger.info('create_cdp')
  elif action == 'draw_cdp':
    logger.info('draw_cdp')
  elif action == 'deposit_cdp':
    logger.info('deposit_cdp')
  elif action in ['repay_cdp', '/kava.cdp.v1beta1.MsgRepayDebt']:
    logger.info('repay_cdp')
  elif action in ['withdraw_cdp', '/kava.cdp.v1beta1.MsgWithdraw']:
    logger.info('withdraw_cdp')
  elif action == 'committee_vote':
    logger.info('committee_vote')
  elif action == 'claimAtomicSwap':
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  elif action in ['claim_hard_reward', 'claim_harvest_reward', '/kava.incentive.v1beta1.MsgClaimHardReward']:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    if chain_id in ['kava-8', 'kava-9']:
      amounts = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))
      amounts =  list(map(lambda item: item['value'], amounts))
    else:
      amounts = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amounts = amounts.split(',')

    hard_amount = list(filter(lambda item: 'hard' in item, amounts))[0]
    hard_amount = Decimal(hard_amount.replace('hard', '')) / Decimal('1000000')
    results.append({'Action': 'LENDING', 'Base': 'HARD', 'Volume': hard_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim HARD of hard lending reward'})
    try:
      kava_amount = list(filter(lambda item: 'ukava' in item, amounts))[0]
      kava_amount = Decimal(kava_amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'LENDING', 'Base': 'KAVA', 'Volume': kava_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim KAVA of hard lending reward'})
    except IndexError as e:
      logger.critical('no KAVA reward on hard')

  elif action in ['claim_usdx_minting_reward', 'claim_reward']:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
    results.append({'Action': 'LENDING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim kava usdx minting reward'})
  elif action in ['claim_delegator_reward', '/kava.incentive.v1beta1.MsgClaimDelegatorReward']:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    if chain_id in ['kava-8', 'kava-9']:
      amounts = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))
      amounts =  list(map(lambda item: item['value'], amounts))
    else:
      amounts = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amounts = amounts.split(',')

    try:
      hard_amount = list(filter(lambda item: 'hard' in item, amounts))[0]
      hard_amount = Decimal(hard_amount.replace('hard', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'HARD', 'Volume': hard_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim delegator reward'})
    except IndexError as e:
      logger.critical('no HARD reward on delegator')

    try:
      swp_amount = list(filter(lambda item: 'swp' in item, amounts))[0]
      swp_amount = Decimal(swp_amount.replace('swp', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'SWP', 'Volume': swp_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim delegator reward'})
    except IndexError as e:
      logger.critical('no SWP reward on delegator')
  elif action in ['createAtomicSwap', '/kava.bep3.v1beta1.MsgCreateAtomicSwap']:
    if fee == 0: return results
    message_attributes = list(filter(lambda item: item['type'] == 'message', events))[0]['attributes']
    sender = list(filter(lambda item: item['key'] == 'sender', message_attributes))[0]['value']
    if sender != address: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  elif action in ['delegate','withdraw_delegator_reward', '/cosmos.staking.v1beta1.MsgDelegate','/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward']:
    try:
      transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
      amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
      amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
    except IndexError as e:
      logger.critical('this time. no auto claim reward.')
  elif action in ['begin_redelegate', '/cosmos.staking.v1beta1.MsgBeginRedelegate']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'begin_redelegate'})
  elif action in ['hard_deposit', 'harvest_deposit']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard deposit'})
  elif action in ['hard_withdraw', 'harvest_withdraw', '/kava.hard.v1beta1.MsgWithdraw']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard withdraw'})
  elif action == 'refundAtomicSwap':
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'refund atomic swap'})
  elif action in ['send', '/cosmos.bank.v1beta1.MsgSend']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'send'})
  elif action in ['begin_unbonding', '/cosmos.staking.v1beta1.MsgUndelegate']:
    try:
      transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
      amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
      amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
      amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
      results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
    except IndexError as e:
      logger.critical('this time. no auto claim reward.')
  elif action == 'vote':
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'vote'})
  elif action == 'hard_borrow':
    # logger.debug(f"events : {events}")
    hard_borrow = list(filter(lambda item: item['type'] == 'hard_borrow', events))[0]
    amount_value = list(filter(lambda item: item['key'] == 'borrow_coins', hard_borrow['attributes']))[0]['value']
    amount, currency = split_amount(amount_value)
    logger.debug(f"borrow amount : {amount} {currency}")
    # initialize
    if currency not in hard_rending_amount:
      hard_rending_amount[currency] = Decimal(0)
    hard_rending_amount[currency] += amount
    results.append({'Action': 'BORROW', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'hard borrow'})
  elif action == 'hard_repay':
    # logger.info(f"events : {events}")
    hard_repay = list(filter(lambda item: item['type'] == 'hard_repay', events))[0]
    amount_value = list(filter(lambda item: item['key'] == 'repay_coins', hard_repay['attributes']))[0]['value']
    amount, currency = split_amount(amount_value)
    logger.debug(f"repay amount : {amount} {currency}")
    hard_rending_amount[currency] -= amount
    if hard_rending_amount[currency] < Decimal(0):
      debut_amount = hard_rending_amount[currency] * -1 # debut = -debut * -1
      hard_rending_amount[currency] = Decimal(0) # hard_rending_amount[currency] + debut_amount = 0
      results.append({'Action': 'SELL', 'Base': currency, 'Volume': debut_amount, 'Price': 0, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'hard repay'})
      amount = amount - debut_amount # repay = all - debut
    if amount > Decimal(0):
      results.append({'Action': 'RETURN', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'hard repay'})
  elif action in ['swap_exact_for_tokens','swap_for_exact_tokens', '/kava.swap.v1beta1.MsgSwapExactForTokens']:
    logger.info(action)
    swap_trade = list(filter(lambda item: item['type'] == 'swap_trade', events))[0]
    logger.debug(swap_trade)
    input_amount_value = list(filter(lambda item: item['key'] == 'input', swap_trade['attributes']))[0]['value']
    input_amount, input_currency = split_amount(input_amount_value)
    output_amount_value = list(filter(lambda item: item['key'] == 'output', swap_trade['attributes']))[0]['value']
    output_amount, output_currency = split_amount(output_amount_value)
    exact = list(filter(lambda item: item['key'] == 'exact', swap_trade['attributes']))[0]['value']
    if exact == 'input':
      price = input_amount / output_amount
      results.append({'Action': "BUY", 'Base': output_currency, 'Volume': output_amount, 'Price': price, 'Counter': input_currency, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'swap'})
    elif exact == 'output':
      price = output_amount / input_amount
      results.append({'Action': "SELL", 'Base': input_currency, 'Volume': input_amount, 'Price': price, 'Counter': output_currency, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'swap'})
    else:
      raise ValueError(f"unknown exact: {exact}")
  elif action == 'swap_deposit':
    logger.info(action)
    logger.debug(f"events : {events}")
    logger.debug(f"swp_lp_amount: {swp_lp_amount}")
    swap_deposit = list(filter(lambda item: item['type'] == 'swap_deposit', events))[0]
    pool_id = list(filter(lambda item: item['key'] == 'pool_id', swap_deposit['attributes']))[0]['value']
    amount_values = list(filter(lambda item: item['key'] == 'amount', swap_deposit['attributes']))[0]['value']
    shares = list(filter(lambda item: item['key'] == 'shares', swap_deposit['attributes']))[0]['value']
    amounts = {}
    for amount_value in amount_values.split(","):
      amount, currency = split_amount(amount_value)
      amounts[currency] = amount
    logger.debug(f"amount: {amount}")

    # initialize
    if pool_id not in swp_lp_amount:
      swp_lp_amount[pool_id] = {}
    if "shares" not in swp_lp_amount[pool_id]:
      swp_lp_amount[pool_id]["shares"] = Decimal("0")
    for currency in amounts.keys():
      if currency not in swp_lp_amount[pool_id]:
        swp_lp_amount[pool_id][currency] = Decimal("0")

    for currency, amount in amounts.items():
      swp_lp_amount[pool_id][currency] += amount
    logger.debug(f"swp_lp_amount: {swp_lp_amount}")
    logger.debug(f"shares: {shares}")
    swp_lp_amount[pool_id]["shares"] += Decimal(shares)
  elif action == 'swap_withdraw':
    logger.info(action)
    logger.debug(f"events : {events}")
    swap_withdraw = list(filter(lambda item: item['type'] == 'swap_withdraw', events))[0]
    pool_id = list(filter(lambda item: item['key'] == 'pool_id', swap_withdraw['attributes']))[0]['value']
    amount_values = list(filter(lambda item: item['key'] == 'amount', swap_withdraw['attributes']))[0]['value']
    shares = list(filter(lambda item: item['key'] == 'shares', swap_withdraw['attributes']))[0]['value']
    amounts = {}
    for amount_value in amount_values.split(","):
      amount, currency = split_amount(amount_value)
      amounts[currency] = amount
    logger.debug(f"amount: {amount}")
    if swp_lp_amount[pool_id]["shares"] - Decimal(shares) < 0:
      raise ValueError("Withdrawals are occurring beyond expectations.")
    swp_lp_amount[pool_id]["shares"] -= Decimal(shares)
    for currency, amount in amounts.items():
      if swp_lp_amount[pool_id][currency] - amount >= 0:
        swp_lp_amount[pool_id][currency] -= amount
      elif swp_lp_amount[pool_id][currency] - amount < 0:
        bonus_amount = amount - swp_lp_amount[pool_id][currency]
        swp_lp_amount[pool_id][currency] -= bonus_amount
        results.append({'Action': 'BONUS', 'Base': currency, 'Volume': bonus_amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'Liquidity Provide Bonus'})
    if swp_lp_amount[pool_id]["shares"] == 0:
      for currency, amount in amounts.items():
        if swp_lp_amount[pool_id][currency] > 0:
          sell_amount = swp_lp_amount[pool_id][currency]
          results.append({'Action': 'SELL', 'Base': currency, 'Volume': sell_amount, 'Price': 0, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'Liquidity Provide Sell'})
  elif action == 'claim_swap_reward':
    logger.info(action)
    logger.debug(f"events : {events}")
    claim_reward = list(filter(lambda item: item['type'] == 'claim_reward', events))[0]
    amount_value = list(filter(lambda item: item['key'] == 'claim_amount', claim_reward['attributes']))[0]['value']
    amount, currency = split_amount(amount_value)
    logger.debug(f"claim amount : {amount} {currency}")
    results.append({'Action': 'BONUS', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'Claim Swap Reward'})
  else:
      raise ValueError('%s: this is undefined action .... %s: txhash' % (action, txhash))

  results = list(map(lambda item: item|{'Timestamp': timestamp, 'Source': 'kava', 'Comment': item['Comment'] + ' https://www.mintscan.io/kava/txs/%s' % txhash}, results))
  #logger.debug(results)
  return results


def main():
  addresses = get_wallet_address()
  for address in addresses:
    create_cryptact_csv(address)


if __name__== '__main__':
  set_root_logger()
  main()
