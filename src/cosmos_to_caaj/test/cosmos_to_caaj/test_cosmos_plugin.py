import unittest
from test_message import *
import os
from cosmos_to_caaj.cosmos_plugin import *
import json
from pathlib import Path

class TestCosmosPlugin(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_as_withdraw_delegator_reward(self):
    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    cosmos = CosmosPlugin()
    caaj = cosmos.get_caajs(v4_withdraw_delegator_reward, 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[0]

    self.assertEqual(caaj['time'], '2021-02-25 01:30:36')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'ATOM': '0.888455'})
    self.assertEqual(caaj['debit_from'], 'cosmos_staking_reward')
    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj['credit_amount'], {'ATOM': '0.888455'})
    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_to'], 'cosmos_staking_reward')

  def test_as_transaction_fee(self):
    v4_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v4.json' % os.path.dirname(__file__)).read_text())
    cosmos = CosmosPlugin()
    caaj = cosmos.get_caajs(v4_withdraw_delegator_reward, 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[1]

    self.assertEqual(caaj['time'], '2021-02-25 01:30:36')
    self.assertEqual(caaj['debit_title'], 'FEE')
    self.assertEqual(caaj['debit_amount'], {'ATOM': '0.0003'})
    self.assertEqual(caaj['debit_from'], 'cosmos_fee')
    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'ATOM': '0.0003'})
    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_to'], 'cosmos_fee')

  def test_as_delegate(self):
    v3_delegate = json.loads(Path('%s/../testdata/delegate_v3.json' % os.path.dirname(__file__)).read_text())
    cosmos = CosmosPlugin()
    caajs = cosmos.get_caajs(v3_delegate, 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')

    caaj_delegate = caajs[0]
    caaj_reward = caajs[1]
  
    self.assertEqual(caaj_delegate['time'], '2020-09-01 19:22:49')
    self.assertEqual(caaj_delegate['debit_title'], 'STAKING')
    self.assertEqual(caaj_delegate['debit_amount'], {'ATOM': '15.799646'})
    self.assertEqual(caaj_delegate['debit_from'], 'cosmos_validator')
    self.assertEqual(caaj_delegate['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj_delegate['credit_title'], 'SPOT')
    self.assertEqual(caaj_delegate['credit_amount'], {'ATOM': '15.799646'})
    self.assertEqual(caaj_delegate['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj_delegate['credit_to'], 'cosmos_validator')

    self.assertEqual(caaj_reward['time'], '2020-09-01 19:22:49')
    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
    self.assertEqual(caaj_reward['debit_amount'], {'ATOM': '0.000016'})
    self.assertEqual(caaj_reward['debit_from'], 'cosmos_staking_reward')
    self.assertEqual(caaj_reward['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj_reward['credit_amount'], {'ATOM': '0.000016'})
    self.assertEqual(caaj_reward['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj_reward['credit_to'], 'cosmos_staking_reward')

  def test_begin_unbonding(self):
    v3_begin_unbonding = json.loads(Path('%s/../testdata/begin_unbonding_v3.json' % os.path.dirname(__file__)).read_text())
    cosmos = CosmosPlugin()
    caajs = cosmos.get_caajs(v3_begin_unbonding, 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')

    caaj_delegate = caajs[0]
    caaj_reward = caajs[1]
  
    self.assertEqual(caaj_delegate['time'], '2021-02-12 11:46:26')
    self.assertEqual(caaj_delegate['debit_title'], 'SPOT')
    self.assertEqual(caaj_delegate['debit_amount'], {'ATOM': '100'})
    self.assertEqual(caaj_delegate['debit_from'], 'cosmos_validator')
    self.assertEqual(caaj_delegate['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_delegate['credit_title'], 'STAKING')
    self.assertEqual(caaj_delegate['credit_amount'], {'ATOM': '100'})
    self.assertEqual(caaj_delegate['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_delegate['credit_to'], 'cosmos_validator')

    self.assertEqual(caaj_reward['time'], '2021-02-12 11:46:26')
    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
    self.assertEqual(caaj_reward['debit_amount'], {'ATOM': '0.017313'})
    self.assertEqual(caaj_reward['debit_from'], 'cosmos_staking_reward')
    self.assertEqual(caaj_reward['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj_reward['credit_amount'], {'ATOM': '0.017313'})
    self.assertEqual(caaj_reward['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_reward['credit_to'], 'cosmos_staking_reward')


  def test_as_send(self):
    v3_send = json.loads(Path('%s/../testdata/send_v3.json' % os.path.dirname(__file__)).read_text())
    cosmos = CosmosPlugin()
    caaj = cosmos.get_caajs(v3_send, 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')[0]

    self.assertEqual(caaj['time'], '2021-01-11 18:19:08')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'ATOM': '1'})
    self.assertEqual(caaj['debit_from'], 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd')
    self.assertEqual(caaj['debit_to'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_title'], 'RECEIVE')
    self.assertEqual(caaj['credit_amount'], {'ATOM': '1'})
    self.assertEqual(caaj['credit_from'], 'cosmos10qcqwfqhgc833hw4e6gk2ajcs8nzjuu03yg3h7')
    self.assertEqual(caaj['credit_to'], 'cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd')

  def test_as_swap_within_batch(self):
    v4_swap_within_batch = json.loads(Path('%s/../testdata/swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())

    cosmos = CosmosPlugin()
    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_swap_transacted):
      caajs = cosmos.get_caajs(v4_swap_within_batch, 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    caaj_swap = caajs[0]
    self.assertEqual(caaj_swap['time'], '2021-09-28 06:47:05')
    self.assertEqual(caaj_swap['debit_title'], 'SPOT')
    self.assertEqual(caaj_swap['debit_amount'], {'ATOM': '6.039087'})
    self.assertEqual(caaj_swap['debit_from'], 'cosmos_liquidity')
    self.assertEqual(caaj_swap['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_swap['credit_title'], 'SPOT')
    self.assertEqual(caaj_swap['credit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '39.940057'})
    self.assertEqual(caaj_swap['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_swap['credit_to'], 'cosmos_liquidity')

    caaj_fee = caajs[1]
    self.assertEqual(caaj_fee['time'], '2021-09-28 06:47:05')
    self.assertEqual(caaj_fee['debit_title'], 'FEE')
    self.assertEqual(caaj_fee['debit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '0.05991'})
    self.assertEqual(caaj_fee['debit_from'], 'cosmos_liquidity')
    self.assertEqual(caaj_fee['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_fee['credit_title'], 'SPOT')
    self.assertEqual(caaj_fee['credit_amount'], {'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC': '0.05991'})
    self.assertEqual(caaj_fee['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_fee['credit_to'], 'cosmos_liquidity')

    v4_swap_within_batch_fail = json.loads(Path('%s/../testdata/swap_within_batch_fail_v4.json' % os.path.dirname(__file__)).read_text())
    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_swap_transacted_fail):
      caajs = cosmos.get_caajs(v4_swap_within_batch_fail, 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')

    caaj_fee = caajs[0]
    self.assertEqual(caaj_fee['time'], '2021-08-25 19:37:54')
    self.assertEqual(caaj_fee['debit_title'], 'FEE')
    self.assertEqual(caaj_fee['debit_amount'], {'ATOM': '0.02'})
    self.assertEqual(caaj_fee['debit_from'], 'cosmos_fee')
    self.assertEqual(caaj_fee['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_fee['credit_title'], 'SPOT')
    self.assertEqual(caaj_fee['credit_amount'], {'ATOM': '0.02'})
    self.assertEqual(caaj_fee['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_fee['credit_to'], 'cosmos_fee')

  def test_as_deposit_within_batch(self):
    v4_deposit_within_batch = json.loads(Path('%s/../testdata/deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())

    cosmos = CosmosPlugin()
    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_deposit_to_pool):
      caajs = cosmos.get_caajs(v4_deposit_within_batch, 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')

    caaj_deposit = caajs[0]
    self.assertEqual(caaj_deposit['time'], '2021-09-30 06:16:43')
    self.assertEqual(caaj_deposit['debit_title'], 'LIQUIDITY')
    self.assertEqual(caaj_deposit['debit_amount'], {'pool32DD066BE949E5FDCC7DC09EBB67C7301D0CA957C2EF56A39B37430165447DAC': '0.000022'})
    self.assertEqual(caaj_deposit['debit_from'], 'cosmos_liquidity')
    self.assertEqual(caaj_deposit['debit_to'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_deposit['credit_title'], 'SPOT')
    self.assertEqual(caaj_deposit['credit_amount'], {'ibc/2181AAB0218EAC24BC9F86BD1364FBBFA3E6E3FCC25E88E3E68C15DC6E752D86': '9', 'ATOM': '0.863882'})
    self.assertEqual(caaj_deposit['credit_from'], 'cosmos1k6udtfc90k8h04aqdp2e69udd52z80lp82xns5')
    self.assertEqual(caaj_deposit['credit_to'], 'cosmos_liquidity')

  def test_as_withdraw_within_batch(self):
    v4_withdraw_within_batch = json.loads(Path('%s/../testdata/withdraw_within_batch_v4.json' % os.path.dirname(__file__)).read_text())

    cosmos = CosmosPlugin()
    with patch.object(Block, 'get_block', new=TestMessage.mock_get_block_withdraw_from_pool):
      caajs = cosmos.get_caajs(v4_withdraw_within_batch, 'cosmos1697eu6zsqnghmac28a2d30y3ffxehpztezgrnq')

    caaj_deposit = caajs[0]
    self.assertEqual(caaj_deposit['time'], '2021-10-04 06:13:53')
    self.assertEqual(caaj_deposit['debit_title'], 'SPOT')
    self.assertEqual(caaj_deposit['debit_amount'], {'ibc/C932ADFE2B4216397A4F17458B6E4468499B86C3BC8116180F85D799D6F5CC1B': '25208.119176', 'ATOM': '1.17456'})
    self.assertEqual(caaj_deposit['debit_from'], 'cosmos_liquidity')
    self.assertEqual(caaj_deposit['debit_to'], 'cosmos1697eu6zsqnghmac28a2d30y3ffxehpztezgrnq')
    self.assertEqual(caaj_deposit['credit_title'], 'LIQUIDITY')
    self.assertEqual(caaj_deposit['credit_amount'], {'poolBD5F1AF7A8B1F068C178F1D637DF126968EC10AB204A10116E320B2B8AF4FAC2': '0.000245'})
    self.assertEqual(caaj_deposit['credit_from'], 'cosmos1697eu6zsqnghmac28a2d30y3ffxehpztezgrnq')
    self.assertEqual(caaj_deposit['credit_to'], 'cosmos_liquidity')

if __name__ == '__main__':
  unittest.main()