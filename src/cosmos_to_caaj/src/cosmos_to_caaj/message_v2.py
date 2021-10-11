from decimal import *
from datetime import datetime as dt
from cosmos_to_caaj.cosmos_util import *
from cosmos_to_caaj.block import *
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.message import *

class MessageV2((Message)):
  def __init__(self, messages_events, tags, height, chain_id):
    self.messages_events = messages_events
    self.tags = tags
    self.height = height
    self.chain_id = chain_id
    self.logs_events = None

  def get_action(self):
    type = self.messages_events['type']

    if type == 'cosmos-sdk/MsgWithdrawDelegationReward':
      action = 'withdraw_delegator_reward'
    elif type == 'cosmos-sdk/MsgDelegate':
      action = 'delegate'
    elif type == 'cosmos-sdk/MsgSend':
      action = 'send'
    elif type == 'cosmos-sdk/MsgMultiSend':
      action = 'multisend'
    elif type == 'cosmos-sdk/MsgBeginRedelegate':
      action = 'begin_redelegate'
    elif type == 'cosmos-sdk/MsgVote':
      action = 'vote'
    else:
      action = super().get_action()

    return action

  def get_result(self):
    action = self.get_action()

    result = {'action': None, 'result': None}
    if action == 'delegate':
      result = self.__as_delegate()
    elif action == 'begin_redelegate':
      result = self.__as_begin_redelegate()
    elif action == 'withdraw_delegator_reward':
      result = self.__as_withdraw_delegator_reward()
    elif action == 'send':
      result = self.__as_send()
    elif action == 'vote':
      result = {'action': 'vote', 'result': None}
    else:
      result = super().get_result()

    return result

  def __as_send(self):
    recipient = self.messages_events['value']['to_address']
    sender = self.messages_events['value']['from_address']
    coin = self.messages_events['value']['amount'][0]['denom']
    coin = 'ATOM' if coin == 'uatom' else coin
    amount = str(CosmosUtil.convert_uamount_amount(self.messages_events['value']['amount'][0]['amount']))

    return {'action': 'send', 'result': {'sender': sender, 'recipient': recipient, 'coin': coin, 'amount': amount}}

  def __as_withdraw_delegator_reward(self):
    amount = CosmosUtil.get_attribute_value(self.tags, 'rewards')
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    return {'action': 'withdraw_delegator_reward', 'result': {'reward_coin': 'ATOM', 'reward_amount': amount}}

  def __as_delegate(self):
    amount = self.messages_events['value']['amount']['amount']
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    result = {'staking_coin': 'ATOM', 'staking_amount': amount}

    return {'action': 'delegate', 'result': result}

  def __as_begin_redelegate(self):
    result = {'staking_coin': 'ATOM', 'staking_amount': '0', 'reward_coin': 'ATOM', 'reward_amount': '0'}
    return {'action': 'delegate', 'result': result}