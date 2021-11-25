import sys
import logging
from decimal import *
from datetime import datetime as dt
import os
from caaj_to_cryptact.caaj_file_handler import *
from caaj_to_cryptact.caaj_to_cryptact import CaajToCryptact
from caaj_to_cryptact.cryptact_file_handler import CryptactFileHandler

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

def set_root_logger():
    root_logger = logging.getLogger(name=None)
    root_logger.setLevel(logging.INFO)
    if not root_logger.hasHandlers():
      fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%dT%H:%M:%S")
      stream_handler = logging.StreamHandler()
      stream_handler.setLevel(logging.INFO)
      stream_handler.setFormatter(fmt)
      root_logger.addHandler(stream_handler)

def read_config():
  f = open(".env.json","r")
  env_dict = json.load(f)
  return env_dict

def get_caaj_file_path():
  if "KAVA_WALLET_ADDRESS" in os.environ:
    return os.environ["CAAJ_FILE_PATH"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["caaj_file_path"]
  else:
    return sys.argv[1].split(",")

def main():
  logger.info('start caaj_to_cryptact')
  caaj_file_paths = get_caaj_file_path()
  cryptact_lines_all = []
  for caaj_file_path in caaj_file_paths:
    caaj_lines = CaajFileHandler.get_caaj_lines(caaj_file_path)
    for i, caaj_line in enumerate(caaj_lines):
      try:
        cryptact_lines = CaajToCryptact.convert(caaj_line)
        cryptact_lines_all.extend(cryptact_lines) if cryptact_lines is not None else None
      except ValueError as e:
        logger.error(f'caaj file line no. {i}')
        raise e

  CryptactFileHandler.write_cryptact_lines(cryptact_lines_all)

if __name__== '__main__':
  set_root_logger()
  main()