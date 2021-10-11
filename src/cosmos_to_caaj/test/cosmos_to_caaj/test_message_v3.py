from sys import version
import unittest
from unittest.mock import *
import os
from cosmos_to_caaj.cosmos_util import CosmosUtil
from cosmos_to_caaj.message import *
from cosmos_to_caaj.message_factory import *
from cosmos_to_caaj.message_v3 import *
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestMessageV3(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_result(self):
    for action_dict in [{'action': 'delegate', 'version': 'v3', 'msg_index': 1},
                        {'action': 'begin_unbonding', 'version': 'v3', 'msg_index': 0}, 
                        {'action': 'send', 'version': 'v3', 'msg_index': 0}]:
      action = action_dict['action']
      msg_index = action_dict['msg_index']
      version = action_dict['version']
      transaction_json = json.loads(Path(f'{os.path.dirname(__file__)}/../testdata/{action}_{version}.json').read_text())
      message = MessageFactory.get_messages(transaction_json)[msg_index]
      result = message.get_result()
      self.assertEqual(result['action'], action)



  def test_as_delegate(self):
    v3_delegate = json.loads(Path('%s/../testdata/delegate_v3.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v3_delegate)[0]
    result = message._Message__as_withdraw_delegator_reward()
    self.assertEqual(result['action'], 'withdraw_delegator_reward')
    self.assertEqual(result['result'], {'reward_coin': 'ATOM', 'reward_amount': '0.000049'})

    message = MessageFactory.get_messages(v3_delegate)[1]
    result = message._MessageV3__as_delegate()
  
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result'], {'staking_coin': 'ATOM', 'staking_amount': '0.000397'})

if __name__ == '__main__':
  unittest.main()