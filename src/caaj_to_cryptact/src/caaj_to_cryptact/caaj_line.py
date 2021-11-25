import json
import logging

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


class CaajLine:
  TIME = 0
  PLATFORM = 1
  TRANSACTION_ID = 2
  DEBIT_TITLE = 3
  DEBIT_AMOUNT = 4
  DEBIT_FROM = 5
  DEBIT_TO = 6
  CREDIT_TITLE = 7
  CREDIT_AMOUNT = 8
  CREDIT_FROM = 9
  CREDIT_TO = 10
  COMMENT = 11

  def __init__(self, line):
    self.time = line[CaajLine.TIME]
    self.platform = line[CaajLine.PLATFORM]
    self.transaction_id = line[CaajLine.TRANSACTION_ID]
    self.debit_title = line[CaajLine.DEBIT_TITLE]
    self.debit_amount = json.loads(line[CaajLine.DEBIT_AMOUNT].replace("'", '"'))
    self.debit_from = line[CaajLine.DEBIT_FROM]
    self.debit_to = line[CaajLine.DEBIT_TO]
    self.credit_title = line[CaajLine.CREDIT_TITLE]
    self.credit_amount = json.loads(line[CaajLine.CREDIT_AMOUNT].replace("'", '"'))
    self.credit_from = line[CaajLine.CREDIT_FROM]
    self.credit_to = line[CaajLine.CREDIT_TO]
    self.comment = line[CaajLine.COMMENT]

  def get_json(self):
    return {'time': self.time, 'platform': self.platform, 'transaction_id': self.transaction_id, 
      'debit_title': self.debit_title, 'debit_amount': self.debit_amount, 'debit_from': self.debit_from, 
      'debit_to': self.debit_to, 'credit_title': self.credit_title, 'credit_amount': self.credit_amount, 
      'credit_from': self.credit_from, 'credit_to': self.credit_to, 'comment': self.comment}

