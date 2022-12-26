from decimal import Decimal
import logging

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

class BalanceSeet:
    def __init__(self):
        self.balance_sheet = {}

    def put_spot_balance_sheet(self, currency: str, amount: Decimal):
      self.balance_sheet.setdefault(currency, {"spot": Decimal("0.0"), "lend": Decimal("0.0"), "borrow": Decimal("0.0")})
      logger.error(f"{currency} {amount}")
      if self.balance_sheet[currency]["spot"] + amount < Decimal("0"):
        logger.error(f'amount become less than 0. current spot amount {self.balance_sheet[currency]["spot"]}. input amount: {amount} currency {currency}')
      self.balance_sheet[currency]["spot"] += amount

    def put_lend_balance_sheet(self, currency: str, amount: Decimal) -> tuple: # (回収額, 利息)のタプルを返す
      self.balance_sheet.setdefault(currency, {"spot": Decimal("0.0"), "lend": Decimal("0.0"), "borrow": Decimal("0.0")})
      result = (abs(amount), 0)
      if self.balance_sheet[currency]["lend"] + amount < Decimal("0"):
        interest = abs(self.balance_sheet[currency]["lend"] + amount)
        result = (self.balance_sheet[currency]["lend"], interest)
        self.balance_sheet[currency]["lend"] = Decimal("0")
        self.balance_sheet[currency]["spot"] += interest
      else:
        self.balance_sheet[currency]["lend"] += amount
      return result

    def put_borrow_balance_sheet(self, currency: str, amount: Decimal) -> tuple: # (返済額, 利息)のタプルを返す
      self.balance_sheet.setdefault(currency, {"spot": Decimal("0.0"), "lend": Decimal("0.0"), "borrow": Decimal("0.0")})
      result = (abs(amount), 0)
      if self.balance_sheet[currency]["borrow"] + amount < Decimal("0"):
        interest = abs(self.balance_sheet[currency]["borrow"] + amount)
        result = (self.balance_sheet[currency]["borrow"], interest)
        self.balance_sheet[currency]["borrow"] = Decimal("0")
        self.balance_sheet[currency]["spot"] -= interest
      else:
        self.balance_sheet[currency]["borrow"] += amount
      return result

    def get_balance_sheet_dict(self) -> dict:
        return self.balance_sheet