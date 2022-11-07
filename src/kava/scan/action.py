import logging
from decimal import Decimal
import re
from typing import Union
from pprint import pprint

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

def split_amount(value:str)-> Union[Decimal, str]:
  amount = re.findall(r'\d+',value)[0]
  currency = value[len(amount):]
  logger.debug(f'split_amount : {amount} {currency}')
  currency_mapping = {
    'ukava':{'Name':'KAVA','precision':6},
    'hard':{'Name':'HARD','precision':6},
    'swp':{'Name':'SWP','precision':6},
    'busd':{'Name':'BUSD','precision':8},
    'usdx':{'Name':'USDX','precision':6},
    'bkava-kavavaloper1ceun2qqw65qce5la33j8zv8ltyyaqqfctl35n4':
      {'Name':'bKAVA','precision':6},
  }
  amount = Decimal(amount) / Decimal(str(10**currency_mapping[currency]["precision"]))
  currency = currency_mapping[currency]["Name"]
  return amount,currency


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
# Delegate Mint Deposit      : /kava.router.v1beta1.MsgDelegateMintDeposit
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
# Withdraw Burn              : /kava.router.v1beta1.MsgWithdrawBurn
# Vote                       : vote
# HARD Withdraw              : hard_borrow
# HARD Repay                 : hard_repay
# Deposit                    : swap_deposit
# Withdraw                   : swap_withdraw
# Claim Swap Reward          : claim_swap_reward
# Comitty Vote               : committee_vote


swp_lp_amount = {} # for reqidity provide calc variable
hard_rending_amount = {} # for rending deposit calc variable

def classify(timestamp, events, fee, txhash, address, chain_id):
  results = []
  params={
    'events':events,
    'fee':fee,
    'chain_id':chain_id,
  }
  global swp_lp_amount
  global hard_rending_amount
  #logger.debug(json.dumps(events, indent=2))
  message = list(filter(lambda item: item['type'] == 'message', events))[0]
  action = list(filter(lambda item: item['key'] == 'action', message['attributes']))[0]['value']
  #logger.debug(events)
  if action in ['create_cdp', '/kava.cdp.v1beta1.MsgCreateCDP']:
    logger.info('create_cdp')
  elif action in ['draw_cdp' , '/kava.cdp.v1beta1.MsgDrawDebt']:
    logger.info('draw_cdp')
  elif action in ['deposit_cdp', '/kava.cdp.v1beta1.MsgDeposit']:
    logger.info('deposit_cdp')
  elif action in ['repay_cdp', '/kava.cdp.v1beta1.MsgRepayDebt']:
    logger.info('repay_cdp')
  elif action in ['withdraw_cdp', '/kava.cdp.v1beta1.MsgWithdraw']:
    logger.info('withdraw_cdp')
  elif action in ['committee_vote']:
    logger.info('committee_vote')
  elif action == '/cosmos.staking.v1beta1.MsgDelegate':
    results += Delegate(events,fee)
  elif action == '/kava.incentive.v1beta1.MsgClaimDelegatorReward':
    results += ClaimDelegatorReward(events,fee,chain_id)
  elif action == '/kava.incentive.v1beta1.MsgClaimEarnReward':
    results += ClaimUSDXReward(events,fee)
  elif action == '/kava.router.v1beta1.MsgDelegateMintDeposit':
    # KavaEarn Deposit (bKava)
    results += MintAndDelegate(events,fee)
  elif action == '/kava.router.v1beta1.MsgWithdrawBurn':
    # KavaEarn Withdraw (bKava)
    logger.info('/kava.router.v1beta1.MsgWithdrawBurn')
    results += BurnAndWithdraw(events,fee)
  elif action == 'claimAtomicSwap':
    results += ClaimAtomicSwap(fee)
  elif action in ['claim_hard_reward', 'claim_harvest_reward', '/kava.incentive.v1beta1.MsgClaimHardReward']:
    results += ClaimHardReward(**params)
  elif action in ['claim_usdx_minting_reward', 'claim_reward']:
    results += ClaimUSDXReward(events,fee)
  elif action in ['claim_delegator_reward', '/kava.incentive.v1beta1.MsgClaimDelegatorReward']:
    results += ClaimDelegatorReward(events,fee,chain_id)
  elif action in ['createAtomicSwap','/kava.bep3.v1beta1.MsgCreateAtomicSwap']:
    if fee == 0: return results
    message_attributes = list(filter(lambda item: item['type'] == 'message', events))[0]['attributes']
    sender = list(filter(lambda item: item['key'] == 'sender', message_attributes))[0]['value']
    if sender != address: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  elif action in ['delegate','withdraw_delegator_reward', '/cosmos.staking.v1beta1.MsgDelegate','/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward']:
    results += Delegate(events,fee)
  elif action in ['begin_redelegate', '/cosmos.staking.v1beta1.MsgBeginRedelegate']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'begin_redelegate'})
  elif action in ['hard_deposit', 'harvest_deposit', '/kava.hard.v1beta1.MsgDeposit']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard deposit'})
  elif action in ['hard_withdraw', 'harvest_withdraw', '/kava.hard.v1beta1.MsgWithdraw']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'hard withdraw'})
  elif action == 'refundAtomicSwap':
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'refund atomic swap'})
  elif action in ['send','/cosmos.bank.v1beta1.MsgSend']:
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'send'})
  elif action in ['begin_unbonding', '/cosmos.staking.v1beta1.MsgUndelegate']:
    results = Undelegate(events,fee)
  elif action == 'vote':
    if fee == 0: return results
    results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'vote'})
  elif action == 'hard_borrow':
    # logger.debug(f"events : {events}")
    results += HardBorrow(**params)
  elif action == 'hard_repay':
    # logger.info(f"events : {events}")
    results += HardReplay(events,fee)
  elif action in ['swap_exact_for_tokens','swap_for_exact_tokens', '/kava.swap.v1beta1.MsgSwapExactForTokens']:
    results += SwapTokens(events,fee)
  elif action == 'swap_deposit':
    SwapDeposit(events,fee)
  elif action == 'swap_withdraw':
    results = SwapWithDraw(events,fee)
  elif action == 'claim_swap_reward':
    results += ClaimSwapReward(events,fee)
  elif re.fullmatch(r'/kava.*', action):
    logger.info(f'skipaction: {action}')
  elif re.fullmatch(r'/cosmos.*', action):
    logger.info(f'skipaction: {action}')
  else:
    raise ValueError('%s: this is undefined action ...' % action)

  results = list(map(lambda item: item|{'Timestamp': timestamp, 'Source': 'kava', 'Comment': item['Comment'] + ' https://www.mintscan.io/kava/txs/%s' % txhash}, results))
  #logger.debug(results)
  return results



def ClaimAtomicSwap(fee,results):
  results = []
  if fee == 0: return results
  results.append({'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'atomic swap fee'})
  return results


def ClaimHardReward(events,chain_id,fee):
  results = []
  transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
  if chain_id == 'kava-8':
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
  return results


def ClaimUSDXReward(events,fee):
  results = []
  transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
  amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
  amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
  results.append({'Action': 'LENDING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim kava usdx minting reward'})
  return results

def ClaimDelegatorReward(events,fee,chain_id):
  results = []
  transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
  if chain_id == 'kava-8':
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
  return results



def MintAndDelegate(events,fee):
  # bkava
  results = []
  coin_received = list(filter(lambda item: item['type'] == 'coinbase', events))[0]
  amount = list(filter(lambda item: item['key'] == 'amount', coin_received['attributes']))[0]['value']
  amount,currency = split_amount(amount) # bkava
  transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
  pprint(transfer)
  amount = list(filter(lambda item: item['key'] == 'amount' and 'ukava' in item['value'], transfer['attributes']))[0]['value']
  amount,currency = split_amount(amount) # kava
  results.append({'Action': 'STAKING', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': currency, 'Comment': 'claim staking reward'})
  return results

def Delegate(events,fee):
  results = []
  try:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
    amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
    results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
  except IndexError as e:
    logger.critical('this time. no auto claim reward.')
  return results


def BurnAndWithdraw(events,fee):
  #bkava
  results = []
  coin_received = list(filter(lambda item: item['type'] == 'burn', events))[0]
  amount = list(filter(lambda item: item['key'] == 'amount', coin_received['attributes']))[0]['value']
  amount,currency = split_amount(amount) # bkava
  # results.append({'Action': 'BORROW', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': currency, 'Comment': 'claim staking reward'})
  transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
  amount = list(filter(lambda item: item['key'] == 'amount' and 'ukava' in item['value'], transfer['attributes']))[0]['value']
  amount,currency = split_amount(amount)
  results.append({'Action': 'STAKING', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': currency, 'Comment': 'claim staking reward'})
  print(results)
  return results


def Undelegate(events,fee):
  results = []
  try:
    transfer = list(filter(lambda item: item['type'] == 'transfer', events))[0]
    amount = list(filter(lambda item: item['key'] == 'amount', transfer['attributes']))[0]['value']
    amount = list(filter(lambda item: 'ukava' in item, amount.split(',')))[0]
    amount = Decimal(amount.replace('ukava', '')) / Decimal('1000000')
    results.append({'Action': 'STAKING', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'claim staking reward'})
  except IndexError as e:
    logger.critical('this time. no auto claim reward.')
  return results


def HardBorrow(events,fee,chain_id):
  results = []
  global swp_lp_amount
  global hard_rending_amount
  hard_borrow = list(filter(lambda item: item['type'] == 'hard_borrow', events))[0]
  amount_value = list(filter(lambda item: item['key'] == 'borrow_coins', hard_borrow['attributes']))[0]['value']
  amount, currency = split_amount(amount_value)
  logger.debug(f"borrow amount : {amount} {currency}")
  # initialize
  if currency not in hard_rending_amount:
    hard_rending_amount[currency] = Decimal(0)
  hard_rending_amount[currency] += amount
  results.append({'Action': 'BORROW', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'hard borrow'})
  return results


def HardReplay(events,fee):
  results = []
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
  return results


def SwapDeposit(events,fee):
  # results = []
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
  # return results


def SwapTokens(events,fee):
  results = []
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
  return results


def ClaimSwapReward(events,fee):
  results = []
  logger.debug(f"events : {events}")
  claim_reward = list(filter(lambda item: item['type'] == 'claim_reward', events))[0]
  amount_value = list(filter(lambda item: item['key'] == 'claim_amount', claim_reward['attributes']))[0]['value']
  amount, currency = split_amount(amount_value)
  logger.debug(f"claim amount : {amount} {currency}")
  results.append({'Action': 'BONUS', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'Claim Swap Reward'})
  return results


def SwapWithDraw(events,fee):
  results = []
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
  return results