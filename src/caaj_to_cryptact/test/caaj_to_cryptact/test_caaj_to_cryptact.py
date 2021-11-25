import unittest
from src.caaj_to_cryptact.caaj_to_cryptact import *
from src.caaj_to_cryptact.caaj_file_handler import *
import os

class TestCaajToCryptact(unittest.TestCase):
  def test_fee(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/simple_kava_caaj.csv' % os.path.dirname(__file__))
    cryptact_line = CaajToCryptact.convert(caaj_lines[0])[0]

    self.assertEqual(cryptact_line.timestamp, '2021-06-11 21:00:00')
    self.assertEqual(cryptact_line.action, 'SENDFEE')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'KAVA')
    self.assertEqual(cryptact_line.volume, '0.0003')
    self.assertEqual(cryptact_line.price, None)
    self.assertEqual(cryptact_line.counter, 'JPY')
    self.assertEqual(cryptact_line.fee, '0')
    self.assertEqual(cryptact_line.feeccy, 'JPY')

  def test_staking_reward(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/simple_kava_caaj.csv' % os.path.dirname(__file__))
    cryptact_line = CaajToCryptact.convert(caaj_lines[8])[0]

    self.assertEqual(cryptact_line.timestamp, '2021-06-18 23:08:11')
    self.assertEqual(cryptact_line.action, 'STAKING')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'KAVA')
    self.assertEqual(cryptact_line.volume, '1.120005')
    self.assertEqual(cryptact_line.price, None)
    self.assertEqual(cryptact_line.counter, 'JPY')
    self.assertEqual(cryptact_line.fee, '0')
    self.assertEqual(cryptact_line.feeccy, 'JPY')

  def test_lending_reward(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/simple_kava_caaj.csv' % os.path.dirname(__file__))
    cryptact_line = CaajToCryptact.convert(caaj_lines[34])[0]

    self.assertEqual(cryptact_line.timestamp, '2021-09-28 06:11:40')
    self.assertEqual(cryptact_line.action, 'LENDING')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'HARD')
    self.assertEqual(cryptact_line.volume, '4.961651')
    self.assertEqual(cryptact_line.price, None)
    self.assertEqual(cryptact_line.counter, 'JPY')
    self.assertEqual(cryptact_line.fee, '0')
    self.assertEqual(cryptact_line.feeccy, 'JPY')

  def test_swap(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/kava_swap_1.csv' % os.path.dirname(__file__))
    cryptact_line = CaajToCryptact.convert(caaj_lines[4])[0]

    self.assertEqual(cryptact_line.timestamp, '2021-10-12 00:48:41')
    self.assertEqual(cryptact_line.action, 'BUY')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.volume, '20')
    self.assertEqual(cryptact_line.price, '6.3323542458276909418522072845503537728008287785237')
    self.assertEqual(cryptact_line.counter, 'KAVA')
    self.assertEqual(cryptact_line.fee, '0')
    self.assertEqual(cryptact_line.feeccy, 'JPY')

  def test_borrow_repay(self):
    BalanceCache.reset()
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/kava_borrow_1.csv' % os.path.dirname(__file__))
    cryptact_line = CaajToCryptact.convert(caaj_lines[112])[0]
    self.assertIsNotNone(cryptact_line)
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '100')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'BORROW')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, None)
    self.assertEqual(cryptact_line.counter, 'JPY')

    cryptact_line = CaajToCryptact.convert(caaj_lines[112])[0]
    self.assertIsNotNone(cryptact_line)
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '200')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'BORROW')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, None)
    self.assertEqual(cryptact_line.counter, 'JPY')

    cryptact_lines = CaajToCryptact.convert(caaj_lines[205])
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '100')
    self.assertIsNotNone(cryptact_lines)
    cryptact_line = cryptact_lines[0]
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'RETURN')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')

    cryptact_lines = CaajToCryptact.convert(caaj_lines[205])
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '0')
    self.assertIsNotNone(cryptact_lines)
    cryptact_line = cryptact_lines[0]
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'RETURN')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')

    cryptact_lines = CaajToCryptact.convert(caaj_lines[205])
    cryptact_line = cryptact_lines[0]
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '0')
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'SELL')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')

    BalanceCache.reset()
    cryptact_line = CaajToCryptact.convert(caaj_lines[112])[0]
    cryptact_lines = CaajToCryptact.convert(caaj_lines[206])
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '0')
    cryptact_line = cryptact_lines[0]
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'RETURN')
    self.assertEqual(cryptact_line.volume, '100')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')

    cryptact_line = cryptact_lines[1]
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'SELL')
    self.assertEqual(cryptact_line.volume, '20')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')

  def test_lend_withdraw(self):
    BalanceCache.reset()
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/kava_borrow_1.csv' % os.path.dirname(__file__))
    cryptact_lines = CaajToCryptact.convert(caaj_lines[36])
    self.assertEqual(BalanceCache.get('kava', 'lend', 'USDX'), '120')
    self.assertIsNone(cryptact_lines)

    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/kava_borrow_1.csv' % os.path.dirname(__file__))
    cryptact_lines = CaajToCryptact.convert(caaj_lines[203])
    self.assertEqual(BalanceCache.get('kava', 'lend', 'USDX'), '20')
    self.assertEqual(len(cryptact_lines), 0)

    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/kava_borrow_1.csv' % os.path.dirname(__file__))
    cryptact_lines = CaajToCryptact.convert(caaj_lines[203])
    self.assertEqual(BalanceCache.get('kava', 'lend', 'USDX'), '0')
    self.assertEqual(len(cryptact_lines), 1)
    cryptact_line = cryptact_lines[0]
    self.assertEqual(cryptact_line.source, 'kava')
    self.assertEqual(cryptact_line.base, 'USDX')
    self.assertEqual(cryptact_line.action, 'LENDING')
    self.assertEqual(cryptact_line.volume, '80')
    self.assertEqual(cryptact_line.price, '0')
    self.assertEqual(cryptact_line.counter, 'JPY')


if __name__ == '__main__':
  unittest.main()