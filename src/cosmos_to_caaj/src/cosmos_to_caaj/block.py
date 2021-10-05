import requests
import json
import base64
from cosmos_to_caaj.cosmos_util import *

class Block:
  def __init__(self, block:json):
    self.block = block
    self.end_block_events = block['result']['end_block_events']
    list(map(lambda x: Block.__decode_dict(x["attributes"]), self.end_block_events))

  @classmethod
  def get_block(cls, height):
    response = requests.get(
        'https://rpc.cosmos.network/block_results',
        params={'height': height})
    block_json = response.json()
    block = Block(block_json)
    return block

  @classmethod
  def __decode_dict(cls, attributes):
    for attribute in attributes:
      for k, v in attribute.items():
        attribute[k] = base64.b64decode(v).decode() if type(v) is str else v

  def get_swap_transacted(self, pool_id, batch_index, msg_index):
    return CosmosUtil.get_event_value(self.end_block_events, 'swap_transacted')

  def get_deposit_to_pool(self, pool_id, batch_index, msg_index):
    return CosmosUtil.get_event_value(self.end_block_events, 'deposit_to_pool')

  def get_withdraw_from_pool(self, pool_id, batch_index, msg_index):
    return CosmosUtil.get_event_value(self.end_block_events, 'withdraw_from_pool')