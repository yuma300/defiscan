import json
from decimal import *
from datetime import datetime as dt
import logging
from kava_to_caaj.kava_util import *
from kava_to_caaj.transaction import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50


class Message:
  def __init__(self, logs_events, messages_events, height, chain_id):
    self.logs_events = logs_events
    self.messages_events = messages_events
    self.height = height
    self.chain_id = chain_id

  def get_action(self):
    event = KavaUtil.get_event_value(self.logs_events, 'message')
    action = KavaUtil.get_attribute_value(event['attributes'], 'action')
    return action

  def get_result(self):
    action = self.get_action()
    logger.debug(action)
    result = {'action': None, 'result': None}
    if action == 'claim_delegator_reward':
      result = self.__as_delegate()
    elif action == 'withdraw_delegator_reward':
      result = self.__as_delegate()
    elif action == 'delegate':
      result = self.__as_delegate()
    elif action == 'begin_redelegate':
      result = self.__as_delegate()
    elif action == 'begin_unbonding':
      result = self.__as_begin_unbonding()
    elif action == 'send':
      result = self.__as_send()
    elif action == 'hard_deposit' or action == 'harvest_deposit':
      result = self.__as_hard_deposit()
    elif action == 'hard_withdraw' or action == 'harvest_withdraw':
      result = self.__as_hard_withdraw()
    elif action == 'hard_repay':
      result = self.__as_hard_repay()
    elif action == 'hard_borrow':
      result = self.__as_hard_borrow()
    elif action == 'claim_hard_reward' or action == 'claim_harvest_reward':
      result = self.__as_claim_hard_reward()
    elif action == 'create_cdp':
      result = self.__as_create_cdp()
    elif action == 'draw_cdp':
      result = self.__as_draw_cdp()
    elif action == 'repay_cdp':
      result = self.__as_repay_cdp()
    elif action == 'deposit_cdp':
      result = self.__as_deposit_cdp()
    elif action == 'withdraw_cdp':
      result = self.__as_withdraw_cdp()
    elif action == 'claim_usdx_minting_reward':
      result = self.__as_claim_usdx_minting_reward()
    elif action == 'claim_reward':
      result = self.__as_claim_usdx_minting_reward()
    elif action == 'createAtomicSwap':
      result = self.__as_createAtomicSwap()
    elif action == 'claimAtomicSwap' or action == 'refundAtomicSwap':
      result = self.__as_claimAtomicSwap()
    elif action == 'swap_exact_for_tokens':
      result = self.__as_swap_exact_for_tokens()
    elif action == 'swap_for_exact_tokens':
      result = self.__as_swap_exact_for_tokens()
    elif action == 'swap_deposit':
      result = self.__as_swap_deposit()
    elif action == 'swap_withdraw':
      result = self.__as_swap_withdraw()
    elif action == 'claim_swap_reward':
      result = self.__as_claim_swap_reward()
    elif action == 'vote' or action == 'committee_vote' or action == 'post_price':
      result = {'action': 'vote', 'result': None}
    else:
      logger.error(f'unknown action: {action}')

    return result

  def __as_withdraw_delegator_reward(self):
    result = {'action':'withdraw_delegator_reward', 'result':{}}
    reward = []

    event = KavaUtil.get_event_value(self.logs_events, 'withdraw_rewards')
    amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
    if event != None:
      amounts = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for amount in amounts:
        amount, coin = KavaUtil.split_amount(amount)
        amount = str(KavaUtil.convert_uamount_amount(amount))
        reward.append({'reward_coin': coin, 'reward_amount': amount})
    result['result']['reward'] = reward

    return result

  def __as_delegate(self):
    result = {'action':'delegate', 'result':{'staking_coin': None, 'staking_amount': None}}
    event = KavaUtil.get_event_value(self.logs_events, 'delegate')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount = str(KavaUtil.convert_uamount_amount(amount))
      result['result']['staking_coin'] = 'KAVA'
      result['result']['staking_amount'] = amount

    reward = []
    # try to find delegate reward
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amounts = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for amount in amounts:
        amount, coin = KavaUtil.split_amount(amount)
        amount = str(KavaUtil.convert_uamount_amount(amount))
        reward.append({'reward_coin': coin, 'reward_amount': amount})
    result['result']['reward'] = reward

    return result

  def __as_begin_unbonding(self):
    event = KavaUtil.get_event_value(self.logs_events, 'unbond')
    amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(KavaUtil.convert_uamount_amount(amount))

    result = {'action':'begin_unbonding', 'result':{'unbonding_coin': 'KAVA', 'unbonding_amount': amount}}
    reward = []
    # try to find delegate reward
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amounts = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for amount in amounts:
        amount, coin = KavaUtil.split_amount(amount)
        amount = str(KavaUtil.convert_uamount_amount(amount))
        reward.append({'reward_coin': coin, 'reward_amount': amount})
    result['result']['reward'] = reward

    return result

  def __as_send(self):
    transfer_event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    amount_coin = KavaUtil.get_attribute_value(transfer_event['attributes'], 'amount')
    amount,coin = KavaUtil.split_amount(amount_coin)
    amount = str(KavaUtil.convert_uamount_amount(amount))
    recipient = KavaUtil.get_attribute_value(transfer_event['attributes'], 'recipient')

    message_event = KavaUtil.get_event_value(self.logs_events, 'message')
    sender = KavaUtil.get_attribute_value(message_event['attributes'], 'sender')

    return {'action': 'send', 'result': {'sender': sender, 'recipient': recipient, 'coin': coin, 'amount': amount}}

  def __as_deposit_within_batch(self):
    deposit_within_batch_event = KavaUtil.get_event_value(self.logs_events, 'deposit_within_batch')

    block = Block.get_block(self.height)
    pool_id = KavaUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'pool_id')
    batch_index = KavaUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'batch_index')
    msg_index = KavaUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'msg_index')        
    deposit_to_pool = block.get_deposit_to_pool(pool_id, batch_index, msg_index)

    pool_coin = KavaUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_denom')
    pool_amount = KavaUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_amount')
    pool_amount = str(KavaUtil.convert_uamount_amount(pool_amount))
    accepted_coins = KavaUtil.get_attribute_value(deposit_to_pool['attributes'], 'accepted_coins').split(',')
    liquidity_coin = {}
    for accepted_coin in accepted_coins:
      amount, coin = KavaUtil.split_amount(accepted_coin)
      liquidity_coin[coin] = str(KavaUtil.convert_uamount_amount(amount))

    return {'action': 'deposit_within_batch', 'result': {'liquidity_coin': liquidity_coin, 'pool_coin': pool_coin, 'pool_amount': pool_amount}}

  def __as_withdraw_within_batch(self):
    withdraw_within_batch_event = KavaUtil.get_event_value(self.logs_events, 'withdraw_within_batch')

    block = Block.get_block(self.height)
    pool_id = KavaUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'pool_id')
    batch_index = KavaUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'batch_index')
    msg_index = KavaUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'msg_index')        
    withdraw_from_pool = block.get_withdraw_from_pool(pool_id, batch_index, msg_index)

    try:
      pool_coin = KavaUtil.get_attribute_value(withdraw_from_pool['attributes'], 'pool_coin_denom')
      pool_amount = KavaUtil.get_attribute_value(withdraw_from_pool['attributes'], 'pool_coin_amount')
      pool_amount = str(KavaUtil.convert_uamount_amount(pool_amount))
      withdraw_coins = KavaUtil.get_attribute_value(withdraw_from_pool['attributes'], 'withdraw_coins').split(',')
    except Exception as e:
      logger.error("invalid withdraw_from_pool. block:")
      logger.error(json.dumps(block.block))
      raise e
    liquidity_coin = {}
    for withdraw_coin in withdraw_coins:
      amount, coin = KavaUtil.split_amount(withdraw_coin)
      liquidity_coin[coin] = str(KavaUtil.convert_uamount_amount(amount))

    return {'action': 'withdraw_within_batch', 'result': {'liquidity_coin': liquidity_coin, 'pool_coin': pool_coin, 'pool_amount': pool_amount}}

  def __as_hard_deposit(self):
    hard_deposit_event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    amount = KavaUtil.get_attribute_value(hard_deposit_event['attributes'], 'amount')
    amount, coin = KavaUtil.split_amount(amount)
    amount = str(KavaUtil.convert_uamount_amount(amount, coin))

    return {'action': 'hard_deposit', 'result': {'hard_deposit_coin': coin, 'hard_deposit_amount': amount}}

  def __as_hard_withdraw(self):
    hard_withdraw_event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    amount = KavaUtil.get_attribute_value(hard_withdraw_event['attributes'], 'amount')
    amount, coin = KavaUtil.split_amount(amount)
    amount = str(KavaUtil.convert_uamount_amount(amount, coin))

    return {'action': 'hard_withdraw', 'result': {'hard_withdraw_coin': coin, 'hard_withdraw_amount': amount}}

  def __as_hard_borrow(self):
    hard_borrow_event = KavaUtil.get_event_value(self.logs_events, 'hard_borrow')
    borrow_coins = KavaUtil.get_attribute_value(hard_borrow_event['attributes'], 'borrow_coins')
    amount, coin = KavaUtil.split_amount(borrow_coins)
    amount = str(KavaUtil.convert_uamount_amount(amount, coin))

    return {'action': 'hard_borrow', 'result': {'hard_borrow_coin': coin, 'hard_borrow_amount': amount}}

  def __as_hard_repay(self):
    hard_repay_event = KavaUtil.get_event_value(self.logs_events, 'hard_repay')
    repay_coins = KavaUtil.get_attribute_value(hard_repay_event['attributes'], 'repay_coins')
    amount, coin = KavaUtil.split_amount(repay_coins)
    amount = str(KavaUtil.convert_uamount_amount(amount, coin))

    return {'action': 'hard_repay', 'result': {'hard_repay_coin': coin, 'hard_repay_amount': amount}}

  def __as_claim_hard_reward(self):
    result = {'action':'claim_hard_reward', 'result':{}}
    reward = []
    # try to find delegate reward
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      claim_amounts = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for amount in claim_amounts:
        amount, coin = KavaUtil.split_amount(amount)
        amount = str(KavaUtil.convert_uamount_amount(amount))
        reward.append({'reward_coin': coin, 'reward_amount': amount})
    result['result']['reward'] = reward

    return result

  def __as_create_cdp(self):
    result = {'action':'create_cdp', 'result':{'deposit_coin':None,'deposit_amount':None, 'draw_coin': None, 'draw_amount':None}}
    event = KavaUtil.get_event_value(self.logs_events, 'cdp_deposit')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['deposit_coin'] = coin
      result['result']['deposit_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    event = KavaUtil.get_event_value(self.logs_events, 'cdp_draw')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['draw_coin'] = coin
      result['result']['draw_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_draw_cdp(self):
    result = {'action':'draw_cdp', 'result':{'draw_coin': None, 'draw_amount':None}}
    event = KavaUtil.get_event_value(self.logs_events, 'cdp_draw')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['draw_coin'] = coin
      result['result']['draw_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_repay_cdp(self):
    result = {'action':'repay_cdp', 'result':{'repay_coin':None,'repay_amount':None, 'withdraw_coin':None, 'withdraw_amount':None}}
    # try to find delegate reward
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amounts = KavaUtil.get_attribute_values(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amounts[0])
      result['result']['repay_coin'] = coin
      result['result']['repay_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

      if len(amounts) == 2:
        amount, coin = KavaUtil.split_amount(amounts[1])
        result['result']['withdraw_coin'] = coin
        result['result']['withdraw_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_deposit_cdp(self):
    result = {'action':'deposit_cdp', 'result':{'deposit_coin':None,'deposit_amount':None}}
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['deposit_coin'] = coin
      result['result']['deposit_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_withdraw_cdp(self):
    result = {'action':'withdraw_cdp', 'result':{'withdraw_coin':None,'withdraw_amount':None}}
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['withdraw_coin'] = coin
      result['result']['withdraw_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_claim_usdx_minting_reward(self):
    result = {'action':'claim_usdx_minting_reward', 'result': {'reward': [{'reward_coin':None,'reward_amount':None}]}}
    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['reward'][0]['reward_coin'] = coin
      result['result']['reward'][0]['reward_amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_createAtomicSwap(self):
    result = {'action':'createAtomicSwap', 'result':{'sender': None, 'recipient': None, 'coin':None, 'amount':None}}
    event = KavaUtil.get_event_value(self.logs_events, 'create_atomic_swap')
    result['result']['sender'] = KavaUtil.get_attribute_value(event['attributes'], 'sender')

    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      result['result']['recipient'] = KavaUtil.get_attribute_value(event['attributes'], 'recipient')
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['coin'] = coin
      result['result']['amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_claimAtomicSwap(self):
    result = {'action':'claimAtomicSwap', 'result':{'sender': None, 'recipient': None, 'coin':None, 'amount':None}}

    event = KavaUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      result['result']['sender'] = KavaUtil.get_attribute_value(event['attributes'], 'sender')
      result['result']['recipient'] = KavaUtil.get_attribute_value(event['attributes'], 'recipient')
      amount = KavaUtil.get_attribute_value(event['attributes'], 'amount')
      amount, coin = KavaUtil.split_amount(amount)
      result['result']['coin'] = coin
      result['result']['amount'] = str(KavaUtil.convert_uamount_amount(amount, coin))

    return result

  def __as_swap_exact_for_tokens(self):
    result = {'action':'swap_exact_for_tokens', 'result':{'input_coin': None, 'input_amount': None, 'output_coin': None, 'output_amount': None, 'fee_coin': None,'fee_amount': None}}
    event = KavaUtil.get_event_value(self.logs_events, 'swap_trade')
    if event != None:
      input = KavaUtil.get_attribute_value(event['attributes'], 'input')
      input_amount, input_coin = KavaUtil.split_amount(input)
      output = KavaUtil.get_attribute_value(event['attributes'], 'output')
      output_amount, output_coin = KavaUtil.split_amount(output)
      fee = KavaUtil.get_attribute_value(event['attributes'], 'fee')
      fee_amount, fee_coin = KavaUtil.split_amount(fee)

      result['result']['input_coin'] = input_coin
      result['result']['input_amount'] = str(KavaUtil.convert_uamount_amount(input_amount, input_coin))
      result['result']['output_coin'] = output_coin
      result['result']['output_amount'] = str(KavaUtil.convert_uamount_amount(output_amount, output_coin))
      result['result']['fee_coin'] = fee_coin
      result['result']['fee_amount'] = str(KavaUtil.convert_uamount_amount(fee_amount, fee_coin))

    return result

  def __as_swap_deposit(self):
    result = {'action':'swap_deposit', 'result':{'share_coin': None,'share_amount': None, 'inputs': None}}
    event = KavaUtil.get_event_value(self.logs_events, 'swap_deposit')
    inputlist = []
    if event != None:
      result['result']['share_coin'] =  KavaUtil.get_attribute_value(event['attributes'], 'pool_id')
      result['result']['share_amount'] =  KavaUtil.get_attribute_value(event['attributes'], 'shares')

      inputs = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for input in inputs:
        amount, coin = KavaUtil.split_amount(input)
        amount = str(KavaUtil.convert_uamount_amount(amount, coin))
        inputlist.append({'input_coin': coin, 'input_amount': amount})

      result['result']['inputs'] = inputlist

    return result

  def __as_swap_withdraw(self):
    result = {'action':'swap_withdraw', 'result':{'share_coin': None,'share_amount': None, 'outputs': None}}
    event = KavaUtil.get_event_value(self.logs_events, 'swap_withdraw')
    inputlist = []
    if event != None:
      result['result']['share_coin'] =  KavaUtil.get_attribute_value(event['attributes'], 'pool_id')
      result['result']['share_amount'] =  KavaUtil.get_attribute_value(event['attributes'], 'shares')

      inputs = KavaUtil.get_attribute_value(event['attributes'], 'amount').split(',')
      for input in inputs:
        amount, coin = KavaUtil.split_amount(input)
        amount = str(KavaUtil.convert_uamount_amount(amount, coin))
        inputlist.append({'output_coin': coin, 'output_amount': amount})

      result['result']['outputs'] = inputlist

    return result


  def __as_claim_swap_reward(self):
    result = {'action':'claim_swap_reward', 'result':{'rewards': None}}
    event = KavaUtil.get_event_value(self.logs_events, 'claim_reward')
    rewardlist = []
    if event != None:
      rewards = KavaUtil.get_attribute_value(event['attributes'], 'claim_amount').split(',')
      for reward in rewards:
        amount, coin = KavaUtil.split_amount(reward)
        amount = str(KavaUtil.convert_uamount_amount(amount, coin))
        rewardlist.append({'reward_coin': coin, 'reward_amount': amount})

      result['result']['rewards'] = rewardlist

    return result