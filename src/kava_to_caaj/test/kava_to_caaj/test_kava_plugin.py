import unittest
from unittest.mock import *
from test.kava_to_caaj.test_config import *
from test.kava_to_caaj.test_message import *
import os
from kava_to_caaj.kava_plugin import *
import json
from pathlib import Path

TestConfig.set_root_logger(TestConfig.INFO)

class TestKavaPlugin(unittest.TestCase):
  """verify get_caaj works fine"""
  def test_as_transaction_fee(self):
    transaction = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(transaction, 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')[2]

    self.assertEqual(caaj['time'], '2021-10-15 01:57:03')
    self.assertEqual(caaj['debit_title'], 'FEE')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '0.0001'})
    self.assertEqual(caaj['debit_from'], 'kava_fee')
    self.assertEqual(caaj['debit_to'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '0.0001'})
    self.assertEqual(caaj['credit_from'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj['credit_to'], 'kava_fee')

  def test_as_delegate(self):
    v8_withdraw_delegator_reward = json.loads(Path('%s/../testdata/withdraw_delegator_reward_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_withdraw_delegator_reward, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-09-06 21:49:27')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '1.298035'})
    self.assertEqual(caaj['debit_from'], 'kava_staking_reward')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '1.298035'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'kava_staking_reward')

    v8_delegate = json.loads(Path('%s/../testdata/delegate_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_delegate, 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')

    caaj_reward = caajs[1]
    caaj_delegate = caajs[0]

    self.assertEqual(caaj_delegate['time'], '2021-10-15 01:57:03')
    self.assertEqual(caaj_delegate['debit_title'], 'STAKING')
    self.assertEqual(caaj_delegate['debit_amount'], {'KAVA': '0.00118'})
    self.assertEqual(caaj_delegate['debit_from'], 'kava_validator')
    self.assertEqual(caaj_delegate['debit_to'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj_delegate['credit_title'], 'SPOT')
    self.assertEqual(caaj_delegate['credit_amount'], {'KAVA': '0.00118'})
    self.assertEqual(caaj_delegate['credit_from'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj_delegate['credit_to'], 'kava_validator')

    self.assertEqual(caaj_reward['time'], '2021-10-15 01:57:03')
    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
    self.assertEqual(caaj_reward['debit_amount'], {'KAVA': '0.000039'})
    self.assertEqual(caaj_reward['debit_from'], 'kava_staking_reward')
    self.assertEqual(caaj_reward['debit_to'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj_reward['credit_amount'], {'KAVA': '0.000039'})
    self.assertEqual(caaj_reward['credit_from'], 'kava1757uf8nmejhlqnmk99n4d9y78taud4neneutus')
    self.assertEqual(caaj_reward['credit_to'], 'kava_staking_reward')

    transaction = json.loads(Path('%s/../testdata/begin_redelegate_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(transaction, 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')

    caaj_reward = caajs[0]

    self.assertEqual(caaj_reward['time'], '2021-09-18 03:21:16')
    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
    self.assertEqual(caaj_reward['debit_amount'], {'KAVA': '3.687213'})
    self.assertEqual(caaj_reward['debit_from'], 'kava_staking_reward')
    self.assertEqual(caaj_reward['debit_to'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj_reward['credit_amount'], {'KAVA': '3.687213'})
    self.assertEqual(caaj_reward['credit_from'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_reward['credit_to'], 'kava_staking_reward')

  def test_as_create_cdp(self):
    v8_create_cdp = json.loads(Path('%s/../testdata/create_cdp_v7.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_create_cdp, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-06-03 14:41:06')
    self.assertEqual(caaj['debit_title'], 'LEND')
    self.assertEqual(caaj['debit_amount'], {'HARD': '10093.653846'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'HARD': '10093.653846'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

    caaj = caajs[1]
    self.assertEqual(caaj['time'], '2021-06-03 14:41:06')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'USDX': '3500'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'BORROW')
    self.assertEqual(caaj['credit_amount'], {'USDX': '3500'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

  def test_as_repay_cdp(self):
    v8_repay_cdp = json.loads(Path('%s/../testdata/repay_cdp_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_repay_cdp, 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-09-09 04:42:15')
    self.assertEqual(caaj['debit_title'], 'BORROW')
    self.assertEqual(caaj['debit_amount'], {'USDX': '10.050333'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'USDX': '10.050333'})
    self.assertEqual(caaj['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

    caaj = caajs[1]
    self.assertEqual(caaj['time'], '2021-09-09 04:42:15')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'BNB': '0.36428994'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_title'], 'LEND')
    self.assertEqual(caaj['credit_amount'], {'BNB': '0.36428994'})
    self.assertEqual(caaj['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

  def test_as_deposit_cdp(self):
    v8_deposit_cdp = json.loads(Path('%s/../testdata/deposit_cdp_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_deposit_cdp, 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-10-02 17:19:14')
    self.assertEqual(caaj['debit_title'], 'LEND')
    self.assertEqual(caaj['debit_amount'], {'XRP': '5063.76309394'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'XRP': '5063.76309394'})
    self.assertEqual(caaj['credit_from'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

  def test_as_withdraw_cdp(self):
    v8_withdraw_cdp = json.loads(Path('%s/../testdata/withdraw_cdp_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_withdraw_cdp, 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-09-09 04:39:11')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'BNB': '1'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_title'], 'LEND')
    self.assertEqual(caaj['credit_amount'], {'BNB': '1'})
    self.assertEqual(caaj['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

  def test_as_claim_usdx_minting_reward(self):
    v7_claim_usdx_minting_reward = json.loads(Path('%s/../testdata/claim_usdx_minting_reward_v7.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v7_claim_usdx_minting_reward, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-06-03 21:54:45')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '3.746212'})
    self.assertEqual(caaj['debit_from'], 'kava_cdp')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'LENDINGREWARD')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '3.746212'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'kava_cdp')

  def test_as_hard_withdraw(self):
    v8_hard_withdraw = json.loads(Path('%s/../testdata/hard_withdraw_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_hard_withdraw, 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')

    caaj = caajs[0]
    self.assertEqual(caaj['time'], '2021-09-20 17:35:47')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'USDX': '1000'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_title'], 'LEND')
    self.assertEqual(caaj['credit_amount'], {'USDX': '1000'})
    self.assertEqual(caaj['credit_from'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

  def test_begin_unbonding(self):
    v8_begin_unbonding = json.loads(Path('%s/../testdata/begin_unbonding_v7.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_begin_unbonding, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')

    caaj_delegate = caajs[0]
    caaj_reward = caajs[1]
  
    self.assertEqual(caaj_delegate['time'], '2021-08-27 10:25:33')
    self.assertEqual(caaj_delegate['debit_title'], 'SPOT')
    self.assertEqual(caaj_delegate['debit_amount'], {'KAVA': '343.546602'})
    self.assertEqual(caaj_delegate['debit_from'], 'kava_validator')
    self.assertEqual(caaj_delegate['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj_delegate['credit_title'], 'STAKING')
    self.assertEqual(caaj_delegate['credit_amount'], {'KAVA': '343.546602'})
    self.assertEqual(caaj_delegate['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj_delegate['credit_to'], 'kava_validator')

    self.assertEqual(caaj_reward['time'], '2021-08-27 10:25:33')
    self.assertEqual(caaj_reward['debit_title'], 'SPOT')
    self.assertEqual(caaj_reward['debit_amount'], {'KAVA': '0.001703'})
    self.assertEqual(caaj_reward['debit_from'], 'kava_staking_reward')
    self.assertEqual(caaj_reward['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj_reward['credit_title'], 'STAKINGREWARD')
    self.assertEqual(caaj_reward['credit_amount'], {'KAVA': '0.001703'})
    self.assertEqual(caaj_reward['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj_reward['credit_to'], 'kava_staking_reward')

  def test_as_send(self):
    v8_send = json.loads(Path('%s/../testdata/send_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(v8_send, 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')[0]

    self.assertEqual(caaj['time'], '2021-10-16 01:26:47')
    self.assertEqual(caaj['debit_title'], 'SEND')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '2.17'})
    self.assertEqual(caaj['debit_from'], 'kava1ys70jvnajkv88529ys6urjcyle3k2j9r24g6a7')
    self.assertEqual(caaj['debit_to'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '2.17'})
    self.assertEqual(caaj['credit_from'], 'kava1dlezgt8undlpvdp0esmzyvxzvc59gkd56vkmea')
    self.assertEqual(caaj['credit_to'], 'kava1ys70jvnajkv88529ys6urjcyle3k2j9r24g6a7')

  def test_as_createAtomicSwap(self):
    transaction = json.loads(Path('%s/../testdata/createAtomicSwap_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(transaction, 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')[0]

    self.assertEqual(caaj['time'], '2021-09-26 12:28:30')
    self.assertEqual(caaj['debit_title'], 'SEND')
    self.assertEqual(caaj['debit_amount'], {'BNB': '1.33428994'})
    self.assertEqual(caaj['debit_from'], 'kava_bc_atomic_swap')
    self.assertEqual(caaj['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'BNB': '1.33428994'})
    self.assertEqual(caaj['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj['credit_to'], 'kava_bc_atomic_swap')

    transaction = json.loads(Path('%s/../testdata/claimAtomicSwap_v4.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(transaction, 'kava1nzq60hrphyr8anvkw6fv93mhafew7ez4tq9ahv')[0]

    self.assertEqual(caaj['time'], '2020-11-10 13:42:52')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'XRP': '99.889'})
    self.assertEqual(caaj['debit_from'], 'kava_bc_atomic_swap')
    self.assertEqual(caaj['debit_to'], 'kava1nzq60hrphyr8anvkw6fv93mhafew7ez4tq9ahv')
    self.assertEqual(caaj['credit_title'], 'RECEIVE')
    self.assertEqual(caaj['credit_amount'], {'XRP': '99.889'})
    self.assertEqual(caaj['credit_from'], 'kava1nzq60hrphyr8anvkw6fv93mhafew7ez4tq9ahv')
    self.assertEqual(caaj['credit_to'], 'kava_bc_atomic_swap')

  def test_as_swap_exact_for_tokens(self):
    v8_swap_exact_for_tokens = json.loads(Path('%s/../testdata/swap_exact_for_tokens_v8.json' % os.path.dirname(__file__)).read_text())

    kava = KavaPlugin()
    caajs = kava.get_caajs(v8_swap_exact_for_tokens, 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    caaj_swap = caajs[0]
    self.assertEqual(caaj_swap['time'], '2021-09-09 04:41:25')
    self.assertEqual(caaj_swap['debit_title'], 'SPOT')
    self.assertEqual(caaj_swap['debit_amount'], {'USDX': '12.290319'})
    self.assertEqual(caaj_swap['debit_from'], 'kava_swap')
    self.assertEqual(caaj_swap['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj_swap['credit_title'], 'SPOT')
    self.assertEqual(caaj_swap['credit_amount'], {'BNB': '0.03'})
    self.assertEqual(caaj_swap['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj_swap['credit_to'], 'kava_swap')

    caaj_fee = caajs[1]
    self.assertEqual(caaj_fee['time'], '2021-09-09 04:41:25')
    self.assertEqual(caaj_fee['debit_title'], 'FEE')
    self.assertEqual(caaj_fee['debit_amount'], {'BNB': '0.000045'})
    self.assertEqual(caaj_fee['debit_from'], 'kava_swap')
    self.assertEqual(caaj_fee['debit_to'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj_fee['credit_title'], 'SPOT')
    self.assertEqual(caaj_fee['credit_amount'], {'BNB': '0.000045'})
    self.assertEqual(caaj_fee['credit_from'], 'kava1mdm5595gw7n2yrfa6fjdrk2xwzn4njkj2akvq4')
    self.assertEqual(caaj_fee['credit_to'], 'kava_swap')

  def test_as_swap_deposit(self):
    transaction = json.loads(Path('%s/../testdata/swap_deposit_v8.json' % os.path.dirname(__file__)).read_text())

    kava = KavaPlugin()
    caajs = kava.get_caajs(transaction, 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    caaj_swap = caajs[0]
    self.assertEqual(caaj_swap['time'], '2021-08-30 17:54:42')
    self.assertEqual(caaj_swap['debit_title'], 'LIQUIDITY')
    self.assertEqual(caaj_swap['debit_amount'], {'busd:usdx': '19155352120'})
    self.assertEqual(caaj_swap['debit_from'], 'kava_swap')
    self.assertEqual(caaj_swap['debit_to'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_swap['credit_title'], 'SPOT')
    self.assertEqual(caaj_swap['credit_amount'], {'BUSD': '1914.40274498', 'USDX':'1918.51883'})
    self.assertEqual(caaj_swap['credit_from'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_swap['credit_to'], 'kava_swap')

  def test_as_swap_withdraw(self):
    transaction = json.loads(Path('%s/../testdata/swap_withdraw_v8.json' % os.path.dirname(__file__)).read_text())

    kava = KavaPlugin()
    caajs = kava.get_caajs(transaction, 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    caaj_swap = caajs[0]
    self.assertEqual(caaj_swap['time'], '2021-08-30 17:52:20')
    self.assertEqual(caaj_swap['debit_title'], 'SPOT')
    self.assertEqual(caaj_swap['debit_amount'], {'SWP': '510.54504', 'USDX': '844.628983'})
    self.assertEqual(caaj_swap['debit_from'], 'kava_swap')
    self.assertEqual(caaj_swap['debit_to'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_swap['credit_title'], 'LIQUIDITY')
    self.assertEqual(caaj_swap['credit_amount'], {'swp:usdx': '655345546'})
    self.assertEqual(caaj_swap['credit_from'], 'kava1tnxjszq48g2k737920cchjqwccrqav053c26l0')
    self.assertEqual(caaj_swap['credit_to'], 'kava_swap')


  def test_as_claim_swap_reward(self):
    transaction = json.loads(Path('%s/../testdata/claim_swap_reward_v8.json' % os.path.dirname(__file__)).read_text())

    kava = KavaPlugin()
    caajs = kava.get_caajs(transaction, 'kava12f45zhguupp5jaa622rpp3n5jyejc4jc3dd5sq')
    caaj_swap = caajs[0]
    self.assertEqual(caaj_swap['time'], '2021-09-15 13:05:53')
    self.assertEqual(caaj_swap['debit_title'], 'SPOT')
    self.assertEqual(caaj_swap['debit_amount'], {'SWP': '830.379251'})
    self.assertEqual(caaj_swap['debit_from'], 'kava_swap')
    self.assertEqual(caaj_swap['debit_to'], 'kava12f45zhguupp5jaa622rpp3n5jyejc4jc3dd5sq')
    self.assertEqual(caaj_swap['credit_title'], 'LIQUIDITYREWARD')
    self.assertEqual(caaj_swap['credit_amount'], {'SWP': '830.379251'})
    self.assertEqual(caaj_swap['credit_from'], 'kava12f45zhguupp5jaa622rpp3n5jyejc4jc3dd5sq')
    self.assertEqual(caaj_swap['credit_to'], 'kava_swap')

  def test_hard_deposit(self):
    v8_hard_deposit = json.loads(Path('%s/../testdata/hard_deposit_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(v8_hard_deposit, 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')[0]

    self.assertEqual(caaj['time'], '2021-10-16 13:03:13')
    self.assertEqual(caaj['debit_title'], 'LEND')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '1513.591717'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '1513.591717'})
    self.assertEqual(caaj['credit_from'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

  def test_hard_borrow(self):
    v8_hard_borrow = json.loads(Path('%s/../testdata/hard_borrow_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(v8_hard_borrow, 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')[0]

    self.assertEqual(caaj['time'], '2021-09-21 00:51:36')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'BUSD': '2637.78595858'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_title'], 'BORROW')
    self.assertEqual(caaj['credit_amount'], {'BUSD': '2637.78595858'})
    self.assertEqual(caaj['credit_from'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

  def test_hard_repay(self):
    v8_hard_repay = json.loads(Path('%s/../testdata/hard_repay_v8.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(v8_hard_repay, 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')[0]

    self.assertEqual(caaj['time'], '2021-10-17 02:29:47')
    self.assertEqual(caaj['debit_title'], 'BORROW')
    self.assertEqual(caaj['debit_amount'], {'BUSD': '1956.12007376'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_title'], 'SPOT')
    self.assertEqual(caaj['credit_amount'], {'BUSD': '1956.12007376'})
    self.assertEqual(caaj['credit_from'], 'kava1vtcpusw3fkzvhxmnuztjdan5v93tw558pp4y47')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

  def test_claim_hard_reward(self):
    v7_hard_reward = json.loads(Path('%s/../testdata/claim_hard_reward_v7.json' % os.path.dirname(__file__)).read_text())
    kava = KavaPlugin()
    caaj = kava.get_caajs(v7_hard_reward, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')[0]
    self.assertEqual(caaj['time'], '2021-08-10 16:27:40')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'HARD': '14.418679'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'LENDINGREWARD')
    self.assertEqual(caaj['credit_amount'], {'HARD': '14.418679'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

    kava = KavaPlugin()
    caaj = kava.get_caajs(v7_hard_reward, 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')[1]
    self.assertEqual(caaj['time'], '2021-08-10 16:27:40')
    self.assertEqual(caaj['debit_title'], 'SPOT')
    self.assertEqual(caaj['debit_amount'], {'KAVA': '24.675275'})
    self.assertEqual(caaj['debit_from'], 'hard_lending')
    self.assertEqual(caaj['debit_to'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_title'], 'LENDINGREWARD')
    self.assertEqual(caaj['credit_amount'], {'KAVA': '24.675275'})
    self.assertEqual(caaj['credit_from'], 'kava1pxvyma3mp6hu0m2c58m54y59acwrwv3yp0r2wl')
    self.assertEqual(caaj['credit_to'], 'hard_lending')

if __name__ == '__main__':
  unittest.main()