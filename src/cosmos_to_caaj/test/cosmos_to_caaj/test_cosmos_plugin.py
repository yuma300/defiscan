import unittest
import os
from cosmos_to_caaj.cosmos_plugin import *
import json
from pathlib import Path

class TestTransaction(unittest.TestCase):
  """verify get_caaj works fine"""
#  def test_as_withdraw_delegator_reward(self):
#    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v4_withdraw_delegator_reward)
#
#    caaj = transaction._Transaction__as_withdraw_delegator_reward('cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[0]
#    self.assertEqual(caaj['time'], '2021-02-25 01:30:36')
#    self.assertEqual(caaj['debit_title'], 'SPOT')
#    self.assertEqual(caaj['debit_amount'], {'ATOM': '0.888455'})
#    self.assertEqual(caaj['debit_from'], 'cosmos_staking_reward')
#    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_title'], 'STAKINGREWARD')
#    self.assertEqual(caaj['credit_amount'], {'ATOM': '0.888455'})
#    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_to'], 'cosmos_staking_reward')
#
#  def test_as_transaction_fee(self):
#    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v4_withdraw_delegator_reward)
#
#    caaj = transaction._Transaction__as_transaction_fee('cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[0]
#    self.assertEqual(caaj['time'], '2021-02-25 01:30:36')
#    self.assertEqual(caaj['debit_title'], 'FEE')
#    self.assertEqual(caaj['debit_amount'], {'ATOM': '0.0003'})
#    self.assertEqual(caaj['debit_from'], 'cosmos_fee')
#    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_title'], 'SPOT')
#    self.assertEqual(caaj['credit_amount'], {'ATOM': '0.0003'})
#    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_to'], 'cosmos_fee')
#
#  def test_as_delegate(self):
#    v3_delegate = json.loads(Path('%s/../testdata/delegate_v3.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v3_delegate)
#    caajs = transaction._Transaction__as_delegate('cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    caaj_delegate = caajs[0]
#    caaj_reward = caajs[1]
#  
#    self.assertEqual(caaj_delegate['time'], '2020-09-01 19:22:49')
#    self.assertEqual(caaj_delegate['debit_title'], 'STAKING')
#    self.assertEqual(caaj_delegate['debit_amount'], {'ATOM': '15.799646'})
#    self.assertEqual(caaj_delegate['debit_from'], 'cosmos_validator')
#    self.assertEqual(caaj_delegate['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj_delegate['credit_title'], 'SPOT')
#    self.assertEqual(caaj_delegate['credit_amount'], {'ATOM': '15.799646'})
#    self.assertEqual(caaj_delegate['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj_delegate['credit_to'], 'cosmos_validator')
#
#    self.assertEqual(caaj_reward['time'], '2020-09-01 19:22:49')
#    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
#    self.assertEqual(caaj_reward['debit_amount'], {'ATOM': '0.000016'})
#    self.assertEqual(caaj_reward['debit_from'], 'cosmos_staking_reward')
#    self.assertEqual(caaj_reward['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
#    self.assertEqual(caaj_reward['credit_amount'], {'ATOM': '0.000016'})
#    self.assertEqual(caaj_reward['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj_reward['credit_to'], 'cosmos_staking_reward')
#
#  def test_as_send(self):
#    v3_send = json.loads(Path('%s/../testdata/send_v3.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v3_send)
#    caaj = transaction._Transaction__as_send('cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[0]
#    self.assertEqual(caaj['time'], '2021-01-11 18:19:08')
#    self.assertEqual(caaj['debit_title'], 'SPOT')
#    self.assertEqual(caaj['debit_amount'], {'ATOM': '1'})
#    self.assertEqual(caaj['debit_from'], 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd')
#    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_title'], 'RECEIVE')
#    self.assertEqual(caaj['credit_amount'], {'ATOM': '1'})
#    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
#    self.assertEqual(caaj['credit_to'], 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd')
#
#  def test_as_swap_within_batch(self):
#    v4_swap_within_batch = json.loads(Path('%s/../testdata/swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v4_swap_within_batch)
#
#    block_json = json.loads(Path('%s/../testdata/block_swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
#    block = Block(block_json)
#    swap_transacted = block.get_swap_transacted(1, 18772, 15644)[0]
#
#    caaj = transaction._Transaction__as_swap_within_batch('cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5', swap_transacted)
#    caaj_swap = caaj[0]
#    self.assertEqual(caaj_swap['time'], '2021-09-28 06:47:05')
#    self.assertEqual(caaj_swap['debit_title'], 'SPOT')
#    self.assertEqual(caaj_swap['debit_amount'], {'ATOM': '6.039087'})
#    self.assertEqual(caaj_swap['debit_from'], 'cosmos_liquidity')
#    self.assertEqual(caaj_swap['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_swap['credit_title'], 'SPOT')
#    self.assertEqual(caaj_swap['credit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '39.940057'})
#    self.assertEqual(caaj_swap['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_swap['credit_to'], 'cosmos_liquidity')
#
#    caaj_fee = caaj[1]
#    self.assertEqual(caaj_fee['time'], '2021-09-28 06:47:05')
#    self.assertEqual(caaj_fee['debit_title'], 'FEE')
#    self.assertEqual(caaj_fee['debit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '0.05991'})
#    self.assertEqual(caaj_fee['debit_from'], 'cosmos_liquidity')
#    self.assertEqual(caaj_fee['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_fee['credit_title'], 'SPOT')
#    self.assertEqual(caaj_fee['credit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '0.05991'})
#    self.assertEqual(caaj_fee['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_fee['credit_to'], 'cosmos_liquidity')
#
#  def test_as_deposit_within_batch(self):
#    v4_deposit_within_batch = json.loads(Path('%s/../testdata/deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
#    transaction = Transaction(v4_deposit_within_batch)
#
#    block_json = json.loads(Path('%s/../testdata/block_deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
#    block = Block(block_json)
#    deposit_to_pool = block.get_deposit_to_pool(5, 18697, 3298)[0]
#
#    caaj_deposit = transaction._Transaction__as_deposit_within_batch('cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5', deposit_to_pool)[0]
#    self.assertEqual(caaj_deposit['time'], '2021-09-30 06:16:43')
#    self.assertEqual(caaj_deposit['debit_title'], 'LIQUIDITY')
#    self.assertEqual(caaj_deposit['debit_amount'], {'pool32DD066BE949E5FDCC7DC09EBB67C7301D0CA957C2EF56A39B37430165447DAC': '22'})
#    self.assertEqual(caaj_deposit['debit_from'], 'cosmos_liquidity')
#    self.assertEqual(caaj_deposit['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_deposit['credit_title'], 'SPOT')
#    self.assertEqual(caaj_deposit['credit_amount'], {'ibc/2181AAB0218EAC24BC9F86BD1364FBBFA3E6E3FCC25E88E3E68C15DC6E752D86': '9', 'ATOM': '0.863882'})
#    self.assertEqual(caaj_deposit['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
#    self.assertEqual(caaj_deposit['credit_to'], 'cosmos_liquidity')
#


if __name__ == '__main__':
  unittest.main()