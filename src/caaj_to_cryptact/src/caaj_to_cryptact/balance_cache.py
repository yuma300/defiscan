import json
import logging
from decimal import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


class BalanceCache:
  cache = {}

  @classmethod
  def add(cls, platform, action, token, amount):
    if platform not in cls.cache:
      cls.cache[platform] = {}
    if action not in cls.cache[platform]:
      cls.cache[platform][action] = {}
    if token in cls.cache[platform][action]: 
      cls.cache[platform][action][token] += Decimal(amount)
    else:
      cls.cache[platform][action][token] = Decimal(amount)

  @classmethod
  def sub(cls, platform, action, token, amount):
    if cls.cache[platform][action][token] < Decimal(amount):
      raise ValueError(f'subtract amount is too big ${platform} ${action} ${token} current amount ${cls.cache[platform][action][token]} subtract amount ${amount}')

    cls.cache[platform][action][token] -= Decimal(amount)

  @classmethod
  def set(cls, platform, action, token, amount):
    if platform not in cls.cache:
      cls.cache[platform] = {}
    if action not in cls.cache[platform]:
      cls.cache[platform][action] = {}
    cls.cache[platform][action][token] = Decimal(amount)

  @classmethod
  def get(cls, platform, action, token):
    return str(cls.cache[platform][action][token])

  @classmethod
  def reset(cls):
    cls.cache = {}
