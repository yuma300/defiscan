import unittest
from caaj_to_cryptact.balance_cache import *
import os

from src.caaj_to_cryptact.balance_cache import BalanceCache

class TestBalanceCache(unittest.TestCase):
  def test_add(self):
    BalanceCache.reset()
    BalanceCache.add('kava', 'borrow', 'USDX', '100')
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '100')
    BalanceCache.add('kava', 'borrow', 'USDX', '100')
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '200')

  def test_sub(self):
    BalanceCache.reset()
    BalanceCache.add('kava', 'borrow', 'USDX', '500')
    BalanceCache.sub('kava', 'borrow', 'USDX', '100')
    self.assertEqual(BalanceCache.get('kava', 'borrow', 'USDX'), '400')

    with self.assertRaises(ValueError):
      BalanceCache.sub('kava', 'borrow', 'USDX', '500')

if __name__ == '__main__':
  unittest.main()