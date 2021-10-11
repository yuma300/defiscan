import json
from decimal import *
from datetime import datetime as dt
import logging
from cosmos_to_caaj.cosmos_util import *
from cosmos_to_caaj.block import *
from cosmos_to_caaj.transaction import *

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
    event = CosmosUtil.get_event_value(self.logs_events, 'message')
    action = CosmosUtil.get_attribute_value(event['attributes'], 'action')
    return action

  def get_result(self):
    action = self.get_action()
    logger.debug(action)
    result = {'action': None, 'result': None}
    if action == 'withdraw_delegator_reward':
      result = self.__as_withdraw_delegator_reward()
    elif action == 'delegate':
      result = self.__as_delegate()
    elif action == 'begin_redelegate':
      result = self.__as_begin_redelegate()
    elif action == 'begin_unbonding':
      result = self.__as_begin_unbonding()
    elif action == 'send':
      result = self.__as_send()
    elif action == 'multisend':
      result = self.__as_multisend()
    elif action == 'swap_within_batch':
      result = self.__as_swap_within_batch()
    elif action == 'deposit_within_batch':
      result = self.__as_deposit_within_batch()
    elif action == 'withdraw_within_batch':
      result = self.__as_withdraw_within_batch()
    elif action == 'transfer':
      result = self.__as_transfer()
    elif action == 'update_client':
      result = {'action': 'update_client', 'result': None}
    elif action == 'recv_packet':
      result = self.__as_recv_packet()
    elif action == 'acknowledge_packet':
      result = {'action': 'acknowledge_packet', 'result': None}
    elif action == 'vote':
      result = {'action': 'vote', 'result': None}
    else:
      logger.error(f'unknown action: {action}')

    return result

  def __as_withdraw_delegator_reward(self):
    event = CosmosUtil.get_event_value(self.logs_events, 'withdraw_rewards')
    amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    return {'action': 'withdraw_delegator_reward', 'result': {'reward_coin': 'ATOM', 'reward_amount': amount}}

  def __as_delegate(self):
    event = CosmosUtil.get_event_value(self.logs_events, 'delegate')
    amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))

    result = {'staking_coin': 'ATOM', 'staking_amount': amount, 'reward_coin': 'ATOM', 'reward_amount': '0'}
    # try to find delegate reward
    event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
      amount = str(CosmosUtil.convert_uamount_amount(amount))          
      result['reward_amount'] = amount

    return {'action': 'delegate', 'result': result}

  def __as_begin_redelegate(self):
    result = {'staking_coin': 'ATOM', 'staking_amount': '0', 'reward_coin': 'ATOM', 'reward_amount': '0'}
    # try to find delegate reward
    event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
      amount = str(CosmosUtil.convert_uamount_amount(amount))          
      result['reward_amount'] = amount

    return {'action': 'delegate', 'result': result}

  def __as_begin_unbonding(self):
    event = CosmosUtil.get_event_value(self.logs_events, 'unbond')
    amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
    amount = str(CosmosUtil.convert_uamount_amount(amount))

    result = {'unbonding_coin': 'ATOM', 'unbonding_amount': amount, 'reward_coin': 'ATOM', 'reward_amount': '0'}
    # try to find delegate reward
    event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    if event != None:
      amount = CosmosUtil.get_attribute_value(event['attributes'], 'amount')
      amount = str(CosmosUtil.convert_uamount_amount(amount))          
      result['reward_amount'] = amount

    return {'action': 'begin_unbonding', 'result': result}

  def __as_send(self):
    transfer_event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    amount_coin = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'amount')
    amount,coin = CosmosUtil.split_amount(amount_coin)
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    recipient = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'recipient')

    message_event = CosmosUtil.get_event_value(self.logs_events, 'message')
    sender = CosmosUtil.get_attribute_value(message_event['attributes'], 'sender')

    return {'action': 'send', 'result': {'sender': sender, 'recipient': recipient, 'coin': coin, 'amount': amount}}

  def __as_multisend(self):
    try:
      if self.chain_id == 'cosmoshub-4':
        senders = self.messages_events['inputs']
        recipients = self.messages_events['outputs']
      else:
        senders = self.messages_events['value']['inputs']
        recipients = self.messages_events['value']['outputs']
      for i in range(len(senders)):
        senders[i]['coins'][0]['amount'] = str(CosmosUtil.convert_uamount_amount(senders[i]['coins'][0]['amount']))
        senders[i]['coins'][0]['denom'] = 'ATOM' if senders[i]['coins'][0]['denom'] == 'uatom' else senders[i]['coins'][0]['denom']
      for i in range(len(recipients)):
        recipients[i]['coins'][0]['amount'] = str(CosmosUtil.convert_uamount_amount(recipients[i]['coins'][0]['amount']))
        recipients[i]['coins'][0]['denom'] = 'ATOM' if recipients[i]['coins'][0]['denom'] == 'uatom' else recipients[i]['coins'][0]['denom']        
    except Exception as e:
      logger.error("multisend failed. self.messages_events:")
      logger.error(json.dumps(self.messages_events))
      raise e

    return {'action': 'multisend', 'result': {'senders': senders, 'recipients': recipients}}

  def __as_swap_within_batch(self):
    swap_within_batch_event = CosmosUtil.get_event_value(self.logs_events, 'swap_within_batch')

    block = Block.get_block(self.height)
    pool_id = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'pool_id')
    batch_index = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'batch_index')
    msg_index = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'msg_index')        
    swap_transacted = block.get_swap_transacted(pool_id, batch_index, msg_index)

    offer_coin = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'offer_coin_denom')
    offer_coin = 'ATOM' if offer_coin == 'uatom' else offer_coin

    demand_coin = CosmosUtil.get_attribute_value(swap_within_batch_event['attributes'], 'demand_coin_denom')
    demand_coin = 'ATOM' if demand_coin == 'uatom' else demand_coin
    
    try:
      offer_amount = CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'exchanged_offer_coin_amount')
      offer_amount = str(CosmosUtil.convert_uamount_amount(offer_amount))
      demand_amount = '0' if Decimal(offer_amount) == Decimal('0') else CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'exchanged_demand_coin_amount')
      demand_amount = str(CosmosUtil.convert_uamount_amount(demand_amount))
      fee_amount = '0' if Decimal(offer_amount) == Decimal('0') else CosmosUtil.get_attribute_value(swap_transacted['attributes'], 'offer_coin_fee_amount')
      fee_amount = str(CosmosUtil.convert_uamount_amount(fee_amount))
    except IndexError as e:
      logger.error("invalid swap_transacted. block:")
      logger.error(json.dumps(block.block))
      raise e

    return {'action': 'swap_within_batch', 'result': {'offer_coin': offer_coin, 'offer_amount': offer_amount, 'demand_coin': demand_coin, 'demand_amount': demand_amount, 'fee_amount': fee_amount}}

  def __as_deposit_within_batch(self):
    deposit_within_batch_event = CosmosUtil.get_event_value(self.logs_events, 'deposit_within_batch')

    block = Block.get_block(self.height)
    pool_id = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'pool_id')
    batch_index = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'batch_index')
    msg_index = CosmosUtil.get_attribute_value(deposit_within_batch_event['attributes'], 'msg_index')        
    deposit_to_pool = block.get_deposit_to_pool(pool_id, batch_index, msg_index)

    pool_coin = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_denom')
    pool_amount = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'pool_coin_amount')
    pool_amount = str(CosmosUtil.convert_uamount_amount(pool_amount))
    accepted_coins = CosmosUtil.get_attribute_value(deposit_to_pool['attributes'], 'accepted_coins').split(',')
    liquidity_coin = {}
    for accepted_coin in accepted_coins:
      amount, coin = CosmosUtil.split_amount(accepted_coin)
      liquidity_coin[coin] = str(CosmosUtil.convert_uamount_amount(amount))

    return {'action': 'deposit_within_batch', 'result': {'liquidity_coin': liquidity_coin, 'pool_coin': pool_coin, 'pool_amount': pool_amount}}

  def __as_withdraw_within_batch(self):
    withdraw_within_batch_event = CosmosUtil.get_event_value(self.logs_events, 'withdraw_within_batch')

    block = Block.get_block(self.height)
    pool_id = CosmosUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'pool_id')
    batch_index = CosmosUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'batch_index')
    msg_index = CosmosUtil.get_attribute_value(withdraw_within_batch_event['attributes'], 'msg_index')        
    withdraw_from_pool = block.get_withdraw_from_pool(pool_id, batch_index, msg_index)

    try:
      pool_coin = CosmosUtil.get_attribute_value(withdraw_from_pool['attributes'], 'pool_coin_denom')
      pool_amount = CosmosUtil.get_attribute_value(withdraw_from_pool['attributes'], 'pool_coin_amount')
      pool_amount = str(CosmosUtil.convert_uamount_amount(pool_amount))
      withdraw_coins = CosmosUtil.get_attribute_value(withdraw_from_pool['attributes'], 'withdraw_coins').split(',')
    except Exception as e:
      logger.error("invalid withdraw_from_pool. block:")
      logger.error(json.dumps(block.block))
      raise e
    liquidity_coin = {}
    for withdraw_coin in withdraw_coins:
      amount, coin = CosmosUtil.split_amount(withdraw_coin)
      liquidity_coin[coin] = str(CosmosUtil.convert_uamount_amount(amount))

    return {'action': 'withdraw_within_batch', 'result': {'liquidity_coin': liquidity_coin, 'pool_coin': pool_coin, 'pool_amount': pool_amount}}

  def __as_transfer(self):
    transfer_event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    amount_coin = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'amount')
    amount,coin = CosmosUtil.split_amount(amount_coin)
    amount = str(CosmosUtil.convert_uamount_amount(amount))

    message_event = CosmosUtil.get_event_value(self.logs_events, 'ibc_transfer')
    sender = CosmosUtil.get_attribute_value(message_event['attributes'], 'sender')
    recipient = CosmosUtil.get_attribute_value(message_event['attributes'], 'receiver')
    
    return {'action': 'transfer', 'result': {'sender': sender, 'recipient': recipient, 'coin': coin, 'amount': amount}}

  def __as_recv_packet(self):
    try:
      recv_packet_event = CosmosUtil.get_event_value(self.logs_events, 'recv_packet')
    except Exception as e:
      logger.error("__as_recv_packet failed recv_packet_event could not get. self.logs_events:")
      logger.error(json.dumps(self.logs_events))  
      raise e

    try:
      packet_data = json.loads(CosmosUtil.get_attribute_value(recv_packet_event['attributes'], 'packet_data'))
    except Exception as e:
      logger.error("__as_recv_packet failed packet_data could not get. recv_packet_event:")
      logger.error(json.dumps(recv_packet_event))  
      raise e

    try:
      transfer_event = CosmosUtil.get_event_value(self.logs_events, 'transfer')
    except Exception as e:
      logger.error("__as_recv_packet failed transfer_event could not get. self.logs_events:")
      logger.error(json.dumps(self.logs_events))  
      raise e

    try:
      amount_coin = CosmosUtil.get_attribute_value(transfer_event['attributes'], 'amount')
    except Exception as e:
      logger.error("__as_recv_packet failed amount_coin could not get. transfer_event:")
      logger.error(json.dumps(transfer_event))  
      raise e

    amount,coin = CosmosUtil.split_amount(amount_coin)
    amount = str(CosmosUtil.convert_uamount_amount(amount))
  
    return {'action': 'recv_packet', 'result': {'sender': packet_data['sender'], 'recipient': packet_data['receiver'], 'coin': coin, 'amount': amount}}