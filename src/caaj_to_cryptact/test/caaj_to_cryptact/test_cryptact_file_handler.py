import unittest
from src.caaj_to_cryptact.caaj_file_handler import *
from src.caaj_to_cryptact.caaj_to_cryptact import *
from src.caaj_to_cryptact.cryptact_file_handler import *
from test.test_config import *
import os

TestConfig.set_root_logger(TestConfig.INFO)

class TestCaajToCryptact(unittest.TestCase):
  def test_write_cryptact_lines(self):
    caaj_lines = CaajFileHandler.get_caaj_lines('%s/../testdata/simple_kava_caaj.csv' % os.path.dirname(__file__))
    cryptact_lines = CaajToCryptact.convert(caaj_lines[0])

    CryptactFileHandler.write_cryptact_lines(cryptact_lines)

if __name__ == '__main__':
  unittest.main()