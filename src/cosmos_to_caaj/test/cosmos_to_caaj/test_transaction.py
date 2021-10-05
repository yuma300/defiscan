import unittest
import os
from cosmos_to_caaj.transaction import *
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestTransaction(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_messages(self):
    multimessages_transaction = json.loads(Path('%s/../testdata/multimessages_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(multimessages_transaction)    
    messages = transaction.get_messages()
    self.assertEqual(messages[0].events[0]['type'], 'message')
    self.assertEqual(messages[1].events[0]['type'], 'denomination_trace')

  def test_get_transaction_id(self):
    v4_success_transaction = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v4_success_transaction)
    transaction_id = transaction.get_transaction_id()
    self.assertEqual(transaction_id, 'c8d6e30e4068ba8986e3eaba0979ab2c2006129cff6b619a4444c43e3bb421d8')

  def test_get_time(self):
    v4_success_transaction = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v4_success_transaction)
    time = transaction.get_time()
    self.assertEqual(time, '2021-02-25 01:30:36')

  def test_get_fee(self):
    v4_success_transaction = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v4_success_transaction)
    fee = transaction.get_fee()
    self.assertEqual(fee, '0.0003')

  def test_get_fail(self):
    v4_success_transaction = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v4_success_transaction)
    self.assertFalse(transaction.get_fail())

    v4_fail_transaction = json.loads(Path('%s/../testdata/fail_v4.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v4_fail_transaction)
    self.assertTrue(transaction.get_fail())

    v3_success_transaction = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v3.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v3_success_transaction)
    self.assertFalse(transaction.get_fail())

    v3_fail_transaction = json.loads(Path('%s/../testdata/fail_v3.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v3_fail_transaction)
    self.assertTrue(transaction.get_fail())

if __name__ == '__main__':
  unittest.main()