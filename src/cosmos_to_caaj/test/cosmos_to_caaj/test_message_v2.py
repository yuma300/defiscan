from sys import version
import unittest
from unittest.mock import *
import os
from cosmos_to_caaj.cosmos_util import CosmosUtil
from cosmos_to_caaj.message import *
from cosmos_to_caaj.message_factory import *
from cosmos_to_caaj.message_v2 import *
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestMessageV2(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_result(self):
    for action_dict in [{'action': 'delegate', 'version': 'v2', 'msg_index': 1}]:
      action = action_dict['action']
      msg_index = action_dict['msg_index']
      version = action_dict['version']
      transaction_json = json.loads(Path(f'{os.path.dirname(__file__)}/../testdata/{action}_{version}.json').read_text())
      message = MessageFactory.get_messages(transaction_json)[msg_index]
      result = message.get_result()
      self.assertEqual(result['action'], action)

  def test_as_delegate(self):
    v2_delegate = json.loads(Path('%s/../testdata/delegate_v2.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v2_delegate)[0]
    result = message._MessageV2__as_withdraw_delegator_reward()
    self.assertEqual(result['action'], 'withdraw_delegator_reward')
    self.assertEqual(result['result'], {'reward_coin': 'ATOM', 'reward_amount': '0.131941'})

    message = MessageFactory.get_messages(v2_delegate)[1]
    result = message._MessageV2__as_delegate()
  
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result'], {'staking_coin': 'ATOM', 'staking_amount': '0.13183'})

  def test_as_send(self):
    v2_send = json.loads(Path('%s/../testdata/send_v2.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v2_send)[0]
    result = message._MessageV2__as_send()
    self.assertEqual(result['action'], 'send')
    self.assertEqual(result['result'], {'sender': 'cosmos155svs6sgxe55rnvs6ghprtqu0mh69kehrn0dqr', 'recipient': 'cosmos1ujgvj5rtfm05609xc6gmzd4q8ydmuy3smtwn29', 'coin': 'ATOM', 'amount': '22.843'})

  def test_as_multisend(self):
    v2_multisend = json.loads(Path('%s/../testdata/multisend_v2.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v2_multisend)[0]
    result = message._Message__as_multisend()
    self.assertEqual(result['result']['senders'], [{'address':'cosmos14kn0kk33szpwus9nh8n87fjel8djx0y0mmswhp', 'coins': [{'denom': 'ATOM', 'amount': '0.0831'}]}])

  def test_as_begin_redelegate(self):
    v2_begin_redelegate = json.loads(Path('%s/../testdata/begin_redelegate_v2.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v2_begin_redelegate)[0]
    result = message._MessageV2__as_begin_redelegate()
  
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result'], {'staking_coin': 'ATOM', 'staking_amount': '0', 'reward_coin': 'ATOM', 'reward_amount': '0'})


if __name__ == '__main__':
  unittest.main()