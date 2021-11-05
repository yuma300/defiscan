import unittest
import os
from kava_to_caaj.transaction import *
import json
from pathlib import Path

class TestTransaction(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_transaction_id(self):
    v8_success_transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v8_success_transaction)
    transaction_id = transaction.get_transaction_id()
    self.assertEqual(transaction_id, '415d5669cdde1e89808932c3e9386169693d73b21478885238e85f19dbe04277')

  def test_get_time(self):
    v8_success_transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v8_success_transaction)
    time = transaction.get_time()
    self.assertEqual(time, '2021-10-15 01:57:03')

  def test_get_fee(self):
    v8_success_transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v8_success_transaction)
    fee = transaction.get_fee()
    self.assertEqual(fee, '0.0001')

  def test_get_fail(self):
    v8_fail_transaction = json.loads(Path('%s/../testdata/fail_v8.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v8_fail_transaction)
    self.assertTrue(transaction.get_fail())

    v8_success_transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    transaction = Transaction(v8_success_transaction)
    self.assertFalse(transaction.get_fail())

if __name__ == '__main__':
  unittest.main()