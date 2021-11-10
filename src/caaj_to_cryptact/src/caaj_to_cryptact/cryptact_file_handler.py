from decimal import *
import logging

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class CryptactFileHandler:
  @classmethod
  def write_cryptact_lines(cls, transaction:json)->list:
    pass
