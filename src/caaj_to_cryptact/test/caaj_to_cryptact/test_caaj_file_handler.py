import unittest
from src.caaj_to_cryptact.caaj_file_handler import *
import os

class TestCaajFileHandler(unittest.TestCase):
  def test_get_caaj_lines(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/simple_kava_caaj.csv' % os.path.dirname(__file__))
    self.assertEqual(len(caaj_lines), 70)
    self.assertEqual(caaj_lines[0].time, '2021-06-11 21:00:00')
    self.assertEqual(caaj_lines[0].platform, 'kava')
    self.assertEqual(caaj_lines[0].transaction_id, '8824d6e909ba7db845f50e8aa673ea5abab60e01a6b7c344df6de876518c1eff')
    self.assertEqual(caaj_lines[0].debit_title, 'FEE')
    self.assertEqual(caaj_lines[0].debit_amount, {'KAVA': '0.0003'})

if __name__ == '__main__':
  unittest.main()