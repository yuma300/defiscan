from sys import version
import unittest
from unittest.mock import *
import os
from cosmos_to_caaj.message import *
from cosmos_to_caaj.message_factory import *
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestMessage(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_result(self):
    # for v4
    for action_dict in [{'action': 'withdraw_delegator_reward', 'version': 'v4', 'msg_index': 0},
                        {'action': 'swap_within_batch', 'version': 'v4', 'msg_index': 0},
                        {'action': 'deposit_within_batch', 'version': 'v4', 'msg_index': 0},
                        {'action': 'withdraw_within_batch', 'version': 'v4', 'msg_index': 0},
                        {'action': 'vote', 'version': 'v4', 'msg_index': 0},
                        {'action': 'acknowledge_packet', 'version': 'v4', 'msg_index': 2},
                        {'action': 'delegate', 'version': 'v3', 'msg_index': 1},
                        {'action': 'begin_unbonding', 'version': 'v3', 'msg_index': 0}, 
                        {'action': 'send', 'version': 'v3', 'msg_index': 0}]:
      action = action_dict['action']
      msg_index = action_dict['msg_index']
      version = action_dict['version']
      transaction_json = json.loads(Path(f'{os.path.dirname(__file__)}/../testdata/{action}_{version}.json').read_text())
      message = MessageFactory.get_messages(transaction_json)[msg_index]
      result = message.get_result()
      self.assertEqual(result['action'], action)

  def test_as_withdraw_delegator_reward(self):
    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_withdraw_delegator_reward)[0]

    result = message._Message__as_withdraw_delegator_reward()
    self.assertEqual(result['action'], 'withdraw_delegator_reward')
    self.assertEqual(result['result'], {'reward_coin': 'ATOM', 'reward_amount': '0.888455'})

  def test_as_begin_redelegate(self):
    v3_begin_redelegate = json.loads(Path('%s/../testdata/begin_redelegate_v3.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v3_begin_redelegate)[0]
    result = message._Message__as_begin_redelegate()
  
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result'], {'staking_coin': 'ATOM', 'staking_amount': '0', 'reward_coin': 'ATOM', 'reward_amount': '0.164288'})

  def test_as_begin_unbonding(self):
    v3_begin_unbonding = json.loads(Path('%s/../testdata/begin_unbonding_v3.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v3_begin_unbonding)[0]
    result = message._Message__as_begin_unbonding()
  
    self.assertEqual(result['action'], 'begin_unbonding')
    self.assertEqual(result['result'], {'unbonding_coin': 'ATOM', 'unbonding_amount': '100', 'reward_coin': 'ATOM', 'reward_amount': '0.017313'})

  def test_as_send(self):
    v3_send = json.loads(Path('%s/../testdata/send_v3.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v3_send)[0]
    result = message._Message__as_send()
    self.assertEqual(result['action'], 'send')
    self.assertEqual(result['result'], {'sender': 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd', 'recipient': 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7', 'coin': 'ATOM', 'amount': '1'})

  def test_as_multisend(self):
    v4_multisend = json.loads(Path('%s/../testdata/multisend_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_multisend)[0]
    result = message._Message__as_multisend()
    self.assertEqual(result['action'], 'multisend')
    self.assertEqual(result['result']['recipients'],  [{'address': 'cosmos144fzpepuvdftv4u4r9kq8t35ap2crruv4u3udz','coins': [{'amount': '26.2707', 'denom': 'ATOM'}]}])
    self.assertEqual(result['result']['senders'], [{'address': 'cosmos1c5dsnqpa8xnuhz55t2xqjh0kn7xuc02q4uhda5', 'coins': [{'amount': '26.2707', 'denom': 'ATOM'}]}])

  @classmethod
  def mock_get_block_swap_transacted(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  @classmethod
  def mock_get_block_swap_transacted_fail(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_swap_within_batch_fail_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  def test_as_swap_within_batch(self):
    v4_swap_within_batch = json.loads(Path('%s/../testdata/swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_swap_within_batch)[0]

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_swap_transacted):
      result = message._Message__as_swap_within_batch()
    self.assertEqual(result['action'], 'swap_within_batch')
    self.assertEqual(result['result'], {'offer_coin': 'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC', 'offer_amount': '39.940057', 'demand_coin': 'ATOM', 'demand_amount': '6.039087', 'fee_amount': '0.05991'})

    v4_swap_within_batch_fail = json.loads(Path('%s/../testdata/swap_within_batch_fail_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_swap_within_batch_fail)[0]

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_swap_transacted_fail):
      result = message._Message__as_swap_within_batch()
    self.assertEqual(result['action'], 'swap_within_batch')
    self.assertEqual(result['result'], {'offer_coin': 'ATOM', 'offer_amount': '0', 'demand_coin': 'ibc/C932ADFE2B4216397A4F17458B6E4468499B86C3BC8116180F85D799D6F5CC1B', 'demand_amount': '0', 'fee_amount': '0'})

  @classmethod
  def mock_get_block_deposit_to_pool(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  def test_as_deposit_within_batch(self):
    v4_deposit_within_batch = json.loads(Path('%s/../testdata/deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_deposit_within_batch)[0]

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_deposit_to_pool):
      result = message._Message__as_deposit_within_batch()
    self.assertEqual(result['action'], 'deposit_within_batch')
    self.assertEqual(result['result'], {'liquidity_coin': {'ATOM': '0.863882', 'ibc/2181AAB0218EAC24BC9F86BD1364FBBFA3E6E3FCC25E88E3E68C15DC6E752D86': '9'}, 'pool_coin': 'pool32DD066BE949E5FDCC7DC09EBB67C7301D0CA957C2EF56A39B37430165447DAC', 'pool_amount': '0.000022'})

  @classmethod
  def mock_get_block_withdraw_from_pool(cls, height):
    block_json = json.loads(Path('%s/../testdata/block_withdraw_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    return block

  def test_as_withdraw_within_batch(self):
    v4_withdraw_within_batch = json.loads(Path('%s/../testdata/withdraw_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_withdraw_within_batch)[0]

    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_withdraw_from_pool):
      result = message._Message__as_withdraw_within_batch()
    self.assertEqual(result['action'], 'withdraw_within_batch')
    self.assertEqual(result['result'], {'liquidity_coin': {'ibc/C932ADFE2B4216397A4F17458B6E4468499B86C3BC8116180F85D799D6F5CC1B': '25208.119176', 'ATOM': '1.17456'}, 'pool_coin': 'poolBD5F1AF7A8B1F068C178F1D637DF126968EC10AB204A10116E320B2B8AF4FAC2', 'pool_amount': '0.000245'})

  def test_as_transfer(self):
    v4_transfer = json.loads(Path('%s/../testdata/transfer_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_transfer)[0]
    result = message._Message__as_transfer()
    self.assertEqual(result['action'], 'transfer')
    self.assertEqual(result['result'], {'sender': 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5', 'recipient': 'sent1k6udtfc90k8h04aqdp2e69udd52z80lpu3s25m', 'coin': 'ibc/42E47A5BA708EBE6E0C227006254F2784E209F4DBD3C6BB77EDC4B29EF875E8E', 'amount': '946.548992'})

  def test_recv_packet(self):
    v4_update_client_recv_packet = json.loads(Path('%s/../testdata/update_client_recv_packet_v4.json' % os.path.dirname(__file__)).read_text())
    message = MessageFactory.get_messages(v4_update_client_recv_packet)[1]
    result = message._Message__as_recv_packet()
    self.assertEqual(result['action'], 'recv_packet')
    self.assertEqual(result['result'], {'sender': 'osmo1k6udtfc90k8h04aqdp2e69udd52z80lp034rxx', 'recipient': 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5', 'coin': 'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC', 'amount': '40'})

if __name__ == '__main__':
  unittest.main()