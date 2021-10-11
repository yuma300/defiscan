from decimal import *
from datetime import datetime as dt
from cosmos_to_caaj.cosmos_util import *
from cosmos_to_caaj.block import *
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.message import *

class MessageV3((Message)):
  def __init__(self, logs_events, messages_events, height, chain_id):
    super().__init__(logs_events, messages_events, height, chain_id)

  def get_result(self):
    action = self.get_action()

    result = {'action': None, 'result': None}
    if action == 'delegate':
      result = self.__as_delegate()
    else:
      result = super().get_result()

    return result

  def __as_delegate(self):
    amount = self.messages_events['value']['amount']['amount']
    amount = str(CosmosUtil.convert_uamount_amount(amount))
    result = {'staking_coin': 'ATOM', 'staking_amount': amount}

    return {'action': 'delegate', 'result': result}
