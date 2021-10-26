from sys import version
import unittest
from unittest.mock import *
import os
from kava_to_caaj.message import *
from kava_to_caaj.message_factory import *
from kava_to_caaj.transaction import *
import json
from pathlib import Path

class TestMessage(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_get_result(self):
    # for v4
    for action_dict in [{'action': 'delegate', 'version': 'v8', 'msg_index': 0}]:
      action = action_dict['action']
      msg_index = action_dict['msg_index']
      version = action_dict['version']
      transaction_json = json.loads(Path(f'{os.path.dirname(__file__)}/../testdata/{action}_{version}.json').read_text())
      message = MessageFactory.get_messages(transaction_json)[msg_index]
      result = message.get_result()
      self.assertEqual(result['action'], action)

  def test_as_withdraw_delegator_reward(self):
    v8_delegate = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_delegate)[0]
    result = message._Message__as_delegate()
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '1.298035'})

  def test_as_delegate(self):
    transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_delegate()
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result']['staking_coin'], 'KAVA')
    self.assertEqual(result['result']['staking_amount'], '0.00118')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '0.000039'})

    transaction = json.loads(Path('%s/../testdata/begin_redelegate_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_delegate()
    self.assertEqual(result['action'], 'delegate')
    self.assertEqual(result['result']['staking_coin'], None)
    self.assertEqual(result['result']['staking_amount'], None)
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '3.687213'})


  def test_begin_unbonding(self):
    v8_begin_unbonding = json.loads(Path('%s/../testdata/begin_unbonding_v7.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_begin_unbonding)[0]
    result = message._Message__as_begin_unbonding()
    self.assertEqual(result['action'], 'begin_unbonding')
    self.assertEqual(result['result']['unbonding_coin'], 'KAVA')
    self.assertEqual(result['result']['unbonding_amount'], '343.546602')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '0.001703'})

  def test_hard_deposit(self):
    v8_hard_deposit = json.loads(Path('%s/../testdata/hard_deposit_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_hard_deposit)[0]
    result = message._Message__as_hard_deposit()
    self.assertEqual(result['action'], 'hard_deposit')
    self.assertEqual(result['result']['hard_deposit_coin'], 'KAVA')
    self.assertEqual(result['result']['hard_deposit_amount'], '1513.591717')

    transaction = json.loads(Path('%s/../testdata/harvest_deposit_v4.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_hard_deposit()
    self.assertEqual(result['action'], 'hard_deposit')
    self.assertEqual(result['result']['hard_deposit_coin'], 'USDX')
    self.assertEqual(result['result']['hard_deposit_amount'], '3610.692343')


  def test_hard_withdraw(self):
    transaction = json.loads(Path('%s/../testdata/hard_withdraw_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_hard_withdraw()
    self.assertEqual(result['action'], 'hard_withdraw')
    self.assertEqual(result['result']['hard_withdraw_coin'], 'USDX')
    self.assertEqual(result['result']['hard_withdraw_amount'], '1000')

    transaction = json.loads(Path('%s/../testdata/harvest_withdraw_v4.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_hard_withdraw()
    self.assertEqual(result['action'], 'hard_withdraw')
    self.assertEqual(result['result']['hard_withdraw_coin'], 'BNB')
    self.assertEqual(result['result']['hard_withdraw_amount'], '292.13977637')

  def test_hard_repay(self):
    v8_hard_repay = json.loads(Path('%s/../testdata/hard_repay_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_hard_repay)[0]
    result = message._Message__as_hard_repay()
    self.assertEqual(result['action'], 'hard_repay')
    self.assertEqual(result['result']['hard_repay_coin'], 'BUSD')
    self.assertEqual(result['result']['hard_repay_amount'], '1956.12007376')

  def test_hard_borrow(self):
    v8_hard_borrow = json.loads(Path('%s/../testdata/hard_borrow_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_hard_borrow)[0]
    result = message._Message__as_hard_borrow()
    self.assertEqual(result['action'], 'hard_borrow')
    self.assertEqual(result['result']['hard_borrow_coin'], 'BUSD')
    self.assertEqual(result['result']['hard_borrow_amount'], '2637.78595858')

  def test_claim_hard_reward(self):
    transaction = json.loads(Path('%s/../testdata/claim_hard_reward_v7.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claim_hard_reward()
    self.assertEqual(result['action'], 'claim_hard_reward')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'HARD', 'reward_amount': '14.418679'})
    self.assertEqual(result['result']['reward'][1], {'reward_coin': 'KAVA', 'reward_amount': '24.675275'})

    transaction = json.loads(Path('%s/../testdata/claim_harvest_reward_v4.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claim_hard_reward()
    self.assertEqual(result['action'], 'claim_hard_reward')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'HARD', 'reward_amount': '23.99439'})

  def test_create_cdp(self):
    v7_create_cdp = json.loads(Path('%s/../testdata/create_cdp_v7.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v7_create_cdp)[0]
    result = message._Message__as_create_cdp()
    self.assertEqual(result['action'], 'create_cdp')
    self.assertEqual(result['result'], {'deposit_coin': 'HARD', 'deposit_amount': '10093.653846', 'draw_coin':'USDX', 'draw_amount':'3500'})

  def test_draw_cdp(self):
    v7_draw_cdp = json.loads(Path('%s/../testdata/draw_cdp_v7.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v7_draw_cdp)[0]
    result = message._Message__as_draw_cdp()
    self.assertEqual(result['action'], 'draw_cdp')
    self.assertEqual(result['result'], {'draw_coin':'USDX', 'draw_amount':'300'})

  def test_repay_cdp(self):
    v8_repay_cdp = json.loads(Path('%s/../testdata/repay_cdp_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_repay_cdp)[0]
    result = message._Message__as_repay_cdp()
    self.assertEqual(result['action'], 'repay_cdp')
    self.assertEqual(result['result'], {'repay_coin': 'USDX', 'repay_amount': '10.050333', 'withdraw_coin':'BNB', 'withdraw_amount':'0.36428994'})

  def test_deposit_cdp(self):
    v7_deposit_cdp = json.loads(Path('%s/../testdata/deposit_cdp_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v7_deposit_cdp)[0]
    result = message._Message__as_deposit_cdp()
    self.assertEqual(result['action'], 'deposit_cdp')
    self.assertEqual(result['result'], {'deposit_coin': 'XRP', 'deposit_amount': '5063.76309394'})

  def test_withdraw_cdp(self):
    v8_withdraw_cdp = json.loads(Path('%s/../testdata/withdraw_cdp_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(v8_withdraw_cdp)[0]
    result = message._Message__as_withdraw_cdp()
    self.assertEqual(result['action'], 'withdraw_cdp')
    self.assertEqual(result['result'], {'withdraw_coin': 'BNB', 'withdraw_amount': '1'})

  def test_as_claim_usdx_minting_reward(self):
    transaction = json.loads(Path('%s/../testdata/claim_usdx_minting_reward_v7.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claim_usdx_minting_reward()
    self.assertEqual(result['action'], 'claim_usdx_minting_reward')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '3.746212'})

    transaction = json.loads(Path('%s/../testdata/claim_reward_v6.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claim_usdx_minting_reward()
    self.assertEqual(result['action'], 'claim_usdx_minting_reward')
    self.assertEqual(result['result']['reward'][0], {'reward_coin': 'KAVA', 'reward_amount': '0.293872'})


  def test_createAtomicSwap(self):
    transaction = json.loads(Path('%s/../testdata/createAtomicSwap_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_createAtomicSwap()
    self.assertEqual(result['action'], 'createAtomicSwap')
    self.assertEqual(result['result'], {'sender':'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4', 'recipient':'kava1eyugkwc74zejgwdwl7mvm7pad4hzdnka4wmdmu','coin': 'BNB', 'amount': '1.33428994'})

    transaction = json.loads(Path('%s/../testdata/createAtomicSwap_v3.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_createAtomicSwap()
    self.assertEqual(result['action'], 'createAtomicSwap')
    self.assertEqual(result['result'], {'sender':'kava1x8cy4tfcxzywqwenttjswlv6x8swhc6hz2xfxq', 'recipient':'kava1eyugkwc74zejgwdwl7mvm7pad4hzdnka4wmdmu','coin': 'BNB', 'amount': '0.1995'})

  def test_claimAtomicSwap(self):
    transaction = json.loads(Path('%s/../testdata/claimAtomicSwap_v4.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claimAtomicSwap()
    self.assertEqual(result['action'], 'claimAtomicSwap')
    self.assertEqual(result['result'], {'sender':'kava1eyugkwc74zejgwdwl7mvm7pad4hzdnka4wmdmu', 'recipient':'kava1nzq60hrphyr8anvkw6fv93mhafew7ez4tq9ahv','coin': 'XRP', 'amount': '99.889'})

    transaction = json.loads(Path('%s/../testdata/refundAtomicSwap_v6.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claimAtomicSwap()
    self.assertEqual(result['action'], 'claimAtomicSwap')
    self.assertEqual(result['result'], {'sender':'kava1eyugkwc74zejgwdwl7mvm7pad4hzdnka4wmdmu', 'recipient':'kava1dfg9r2n12m9abhet34k3xtju9vbndkuieqlojg','coin': 'BNB', 'amount': '500'})


  def test_swap_exact_for_tokens(self):
    transaction = json.loads(Path('%s/../testdata/swap_exact_for_tokens_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_swap_exact_for_tokens()
    self.assertEqual(result['action'], 'swap_exact_for_tokens')
    self.assertEqual(result['result'], {'input_coin': 'BNB', 'input_amount': '0.03', 'output_coin': 'USDX', 'output_amount': '12.290319', 'fee_coin': 'BNB','fee_amount': '0.000045'})

    transaction = json.loads(Path('%s/../testdata/swap_for_exact_tokens_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_swap_exact_for_tokens()
    self.assertEqual(result['action'], 'swap_exact_for_tokens')
    self.assertEqual(result['result'], {'input_coin': 'BUSD', 'input_amount': '13987.92220598', 'output_coin': 'USDX', 'output_amount': '14238.68', 'fee_coin': 'BUSD','fee_amount': '20.98188331'})

  def test_swap_deposit(self):
    transaction = json.loads(Path('%s/../testdata/swap_deposit_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_swap_deposit()
    self.assertEqual(result['action'], 'swap_deposit')
    self.assertEqual(result['result']['share_coin'], 'busd:usdx')
    self.assertEqual(result['result']['share_amount'], '19155352120')
    self.assertEqual(result['result']['inputs'][0], {'input_coin': 'BUSD','input_amount': '1914.40274498'})
    self.assertEqual(result['result']['inputs'][1], {'input_coin': 'USDX', 'input_amount': '1918.51883'})

  def test_swap_withdraw(self):
    transaction = json.loads(Path('%s/../testdata/swap_withdraw_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_swap_withdraw()
    self.assertEqual(result['action'], 'swap_withdraw')
    self.assertEqual(result['result']['share_coin'], 'swp:usdx')
    self.assertEqual(result['result']['share_amount'], '655345546')
    self.assertEqual(result['result']['outputs'][0], {'output_coin': 'SWP','output_amount': '510.54504'})
    self.assertEqual(result['result']['outputs'][1], {'output_coin': 'USDX', 'output_amount': '844.628983'})

  def test_claim_swap_reward(self):
    transaction = json.loads(Path('%s/../testdata/claim_swap_reward_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_claim_swap_reward()
    self.assertEqual(result['action'], 'claim_swap_reward')
    self.assertEqual(result['result']['rewards'][0], {'reward_coin': 'SWP','reward_amount': '830.379251'})

  def test_send(self):
    transaction = json.loads(Path('%s/../testdata/send_v8.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_send()
    self.assertEqual(result['action'], 'send')
    self.assertEqual(result['result'], {'sender':'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea', 'recipient':'kava1ys70jvnajkv88529ys6urjcyle3k2j9r24g6a7','coin': 'KAVA', 'amount': '2.17'})

    transaction = json.loads(Path('%s/../testdata/send_v2.json' % os.path.dirname(__file__)).read_text())

    message = MessageFactory.get_messages(transaction)[0]
    result = message._Message__as_send()
    self.assertEqual(result['action'], 'send')
    self.assertEqual(result['result'], {'sender':'kava1k760ypy9tzhp6l2rmg06sq4n74z0d3relc549c', 'recipient':'kava1nzq60hrphyr8anvkw6fv93mhafew7ez4tq9ahv','coin': 'KAVA', 'amount': '13.5'})


if __name__ == '__main__':
  unittest.main()