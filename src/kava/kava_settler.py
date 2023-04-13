import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt
import  pytz
import datetime
import re
import os
import logging
import re
from typing import Tuple
from financial_tools.balance_sheet import BalanceSeet
from financial_tools.temporary_deposit import TemporaryDeposit
try:
  from financial_tools.extratx_dict import extratx_dict
except:
  raise Exception("execute\n $cp extratx_dict.py_templrate extratx_dict.py")

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
balance_sheet = BalanceSeet()
temporary_deposit = TemporaryDeposit()

def set_root_logger():
  root_logget = logging.getLogger(name=None)
  root_logget.setLevel(logging.INFO)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  root_logget.addHandler(stream_handler)

def read_config():
  f = open(".env.json","r")
  env_dict = json.load(f)
  return env_dict

def get_wallet_address():
  if "KAVA_WALLET_ADDRESS" in os.environ:
    return os.environ["KAVA_WALLET_ADDRESS"].split(",")
  elif os.path.exists(os.getcwd()+"/.env.json"):
    return read_config()["address"]
  else:
    return sys.argv[1].split(",")

def split_amount(value:str) -> Tuple:
  amount = re.findall(r'\d+',value)[0]
  currency = value.replace(amount, '')
  logger.debug(f'split_amount : {amount} {currency}')
  currency_mapping = {
    'ukava':{'Name':'KAVA','precision':6},
    'hard':{'Name':'HARD','precision':6},
    'swp':{'Name':'SWP','precision':6},
    'busd':{'Name':'BUSD','precision':8},
    'usdx':{'Name':'USDX','precision':6},
    'xrpb':{'Name':'XRP','precision':8},
    'bnb':{'Name':'BNB','precision':8},
    'ibc/799FDD409719A1122586A629AE8FCA17380351A51C1F47A80A1B8E7F2A491098':{'Name':'AKT','precision':6},
  }
  amount = Decimal(amount) / Decimal(str(10**currency_mapping[currency]["precision"]))
  currency = currency_mapping[currency]["Name"]
  return amount,currency

def get_fee(transaction: dict) -> Decimal:
  fee = Decimal("0")
  try:
    if transaction['header']['chain_id'] in ['kava-9', 'kava_2222-10']:
      if len(transaction['data']["tx"]["auth_info"]["fee"]["amount"]) == 1:
        fee = Decimal(transaction['data']["tx"]["auth_info"]["fee"]["amount"][0]["amount"]) / Decimal("1000000")
      elif len(transaction['data']["tx"]["auth_info"]["fee"]["amount"]) > 1:
        raise ValueError(f"invalid fee data")
    else:
      if len(transaction['data']["tx"]["value"]["fee"]["amount"]) == 1:
        fee = Decimal(transaction['data']["tx"]["value"]["fee"]["amount"][0]["amount"]) / Decimal("1000000")
      elif len(transaction['data']["tx"]["value"]["fee"]["amount"]) > 1:
        raise ValueError(f"invalid fee data")
  except Exception as e:
    raise ValueError(json.dumps(transaction, indent=2))
  return fee

def set_fee(fee: Decimal, results: list, timestamp: str, txhash: str):
  if fee != Decimal("0.0"):
    results.append({'executed_at': timestamp, 'type': 'pay', 'in_token': None, 'in_amount': None, 'out_token': 'KAVA', 'out_amount': fee, 'market_value': None, 'tags': None, 'comment': f'self transfer https://www.mintscan.io/kava/txs/{txhash}'})
    balance_sheet.put_spot_balance_sheet("KAVA", - fee)

def has_event(events: dict, type: str) -> bool:
  event = list(filter(lambda x: x["type"] == type, events))
  if len(event) > 0:
    return True
  else:
    return False

def get_event(events: dict, type: str):
  event = list(filter(lambda x: x["type"] == type, events))
  if len(event) != 1:
    raise ValueError(f"invalid {type} events in a transaction")
  return event[0]

def get_attribute(attributes: dict, key: str):
  attribute = list(filter(lambda x: x["key"] == key, attributes))
  if len(attribute) != 1:
    raise ValueError(f"invalid: {key} in a attributes")
  return attribute[0]


def insert_extra_tx(results: list, timestamp_dt: dt):
  for extratx in extratx_dict:
    if dt.strptime(extratx["executed_at"], '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone('Asia/Tokyo')) < timestamp_dt:
      timestamp = datetime.datetime.strftime(timestamp_dt, '%Y-%m-%d %H:%M:%S')
      results.append(extratx)
      extratx_dict.remove(extratx)
      action = extratx["type"]
      in_amount = Decimal(extratx["in_amount"]) if extratx["in_amount"] is not None else Decimal('0')
      price = Decimal(extratx["out_amount"]) if extratx["out_amount"] is not None else Decimal('0')
      out_token = extratx["out_token"]
      base = extratx["in_token"]
      if action in ["deposit", "withdraw", "obtain"]:
        balance_sheet.put_spot_balance_sheet(base, in_amount)
      elif action == "recover":
        lend_result = balance_sheet.put_lend_balance_sheet(base, - in_amount)
        if lend_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': base, 'in_amount': lend_result[1], 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'lend interest from extratx'})
      elif action == "trade":
        balance_sheet.put_spot_balance_sheet(base, - in_amount)
        balance_sheet.put_spot_balance_sheet(out_token, in_amount * price)
      elif action == "repay":
        borrow_result = balance_sheet.put_borrow_balance_sheet(base, - in_amount)
        if borrow_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'PAY', 'in_token': None, 'in_amount': None, 'out_token': out_token, 'out_amount': borrow_result[1], 'market_value': None, 'tags': None, 'comment': f'borrow interest from extratx'})

def create_cryptact_csv(address):
  results = []
  transactions = []
  decoder = json.JSONDecoder()
  read_file_name = '%s/transactions_%s.txt' % (os.path.dirname(__file__), address)
  with open(read_file_name, 'r') as f:
    line = f.readline()
    while line:
      line = json.loads(line)
      if "code" in line["data"] and line["data"]["code"] != 0:
        logger.debug(f"this transaction is error hash: {line['data']['txhash']}")
      else:
        transactions.append(line)
      line = f.readline()


  transactions.reverse()

  for transaction in transactions:
    #logger.debug(transaction)
    #logger.debug(json.dumps(transaction['header'], indent=2))
    #logger.debug(json.dumps(transaction, indent=2))
    #chain_id = transaction['header']['chain_id']
    timestamp = dt.strptime(transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp_datetime = timestamp.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    timestamp = datetime.datetime.strftime(timestamp_datetime, '%Y-%m-%d %H:%M:%S')
    txhash = transaction['data']['txhash']
    fee = get_fee(transaction)
    raw_logs = json.loads(transaction['data']['raw_log'])
    insert_extra_tx(results, timestamp_datetime)
    for raw_log in raw_logs:
      message_event = get_event(raw_log["events"], "message")
      action = get_attribute(message_event["attributes"], "action")["value"]
      if action in ["send", "/cosmos.bank.v1beta1.MsgSend"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        sender_address = get_attribute(transfer_event["attributes"], "sender")["value"]
        receiver_address = get_attribute(transfer_event["attributes"], "recipient")["value"]
        if sender_address == address: # 出金の場合
          results.append({'executed_at': timestamp, 'type': 'withdraw', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'send https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet(currency, - amount)
          balance_sheet.put_spot_balance_sheet("KAVA", - fee)
          set_fee(fee, results, timestamp, txhash)
        elif receiver_address == address: # 入金の場合
          results.append({'executed_at': timestamp, 'type': 'deposit', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'receive https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet(currency, amount)
      elif action in ["createAtomicSwap", "/kava.bep3.v1beta1.MsgCreateAtomicSwap"]: # BEP3 Atomic Swap
        if has_event(raw_log["events"], "create_atomic_swap"):
          create_atomic_event = get_event(raw_log["events"], "create_atomic_swap")
          receiver_address = get_attribute(create_atomic_event["attributes"], "recipient")["value"]
        else:
          raise ValueError("invalid atomic swap data")
        atomic_swap_id = get_attribute(create_atomic_event["attributes"], "atomic_swap_id")["value"]
        temporary_deposit.push(atomic_swap_id, create_atomic_event)
        amount = get_attribute(create_atomic_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        sender_address = get_attribute(create_atomic_event["attributes"], "sender")["value"]
        receiver_address = get_attribute(create_atomic_event["attributes"], "recipient")["value"]
        if sender_address == receiver_address:
          results.append({'executed_at': timestamp, 'type': 'pay', 'in_token': None, 'in_amount': None, 'out_token': 'KAVA', 'out_amount': fee, 'market_value': None, 'tags': None, 'comment': f'self transfer https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet("KAVA", -fee)
        elif sender_address == address:
          set_fee(fee, results, timestamp, txhash)
          results.append({'executed_at': timestamp, 'type': 'withdraw', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'send https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet(currency, - amount)
        elif receiver_address == address:
          results.append({'executed_at': timestamp, 'type': 'deposit', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'receive https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet(currency, amount)
      elif action in ["refundAtomicSwap", "claimAtomicSwap", "/kava.bep3.v1beta1.MsgClaimAtomicSwap"]: # BEP3 Refund
        if has_event(raw_log["events"], "refund_atomic_swap"):
          refund_atomic_event = get_event(raw_log["events"], "refund_atomic_swap")
          atomic_swap_id = get_attribute(refund_atomic_event["attributes"], "atomic_swap_id")["value"]
          atomic_swap = temporary_deposit.get(atomic_swap_id)
          sender_address = get_attribute(atomic_swap["attributes"], "sender")["value"]
          receiver_address = get_attribute(atomic_swap["attributes"], "recipient")["value"]
          amount = get_attribute(atomic_swap["attributes"], "amount")["value"]
          amount, currency = split_amount(amount)
          if sender_address == address:
            set_fee(fee, results, timestamp, txhash)
            results.append({'executed_at': timestamp, 'type': 'deposit', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'send https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, amount)
          elif receiver_address == address:
            results.append({'executed_at': timestamp, 'type': 'withdraw', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'receive https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, - amount)
          else:
            raise ValueError("invalid refund atomic swap type")
        elif has_event(raw_log["events"], "claim_atomic_swap"):
          claim_atomic_swap = get_event(raw_log["events"], "claim_atomic_swap")
          atomic_swap_id = get_attribute(claim_atomic_swap["attributes"], "atomic_swap_id")["value"]
          if temporary_deposit.has(atomic_swap_id):
            continue
          else:
            transfer = get_event(raw_log["events"], "transfer")
            amount = get_attribute(transfer["attributes"], "amount")["value"]
            amount, currency = split_amount(amount)
            results.append({'executed_at': timestamp, 'type': 'deposit', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'send https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, amount)
        else:
          raise ValueError("invalid refund atomic swap type")
      elif action in ["create_cdp", "/kava.cdp.v1beta1.MsgCreateCDP"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        if len(amounts) != 2:
          raise ValueError("not two amounts")
        set_fee(fee, results, timestamp, txhash)
        for amount in amounts:
          amount, currency = split_amount(amount["value"])
          if currency.lower() == "usdx":
            results.append({'executed_at': timestamp, 'type': 'borrow', 'in_token': currency, 'in_amount': amount, 'out_token': f'borrow{currency}', 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'cdp create https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_borrow_balance_sheet(currency, amount)
            balance_sheet.put_spot_balance_sheet("KAVA", -fee)
          else:
            lend_result = balance_sheet.put_lend_balance_sheet(currency, amount)
            results.append({'executed_at': timestamp, 'type': 'lend', 'in_token': f'lend{currency}', 'in_amount': lend_result[0], 'out_token': currency, 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp create https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["deposit_cdp", "/kava.cdp.v1beta1.MsgDeposit"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        lend_result = balance_sheet.put_lend_balance_sheet(currency, amount)
        results.append({'executed_at': timestamp, 'type': 'lend', 'in_token': f'lend{currency}', 'in_amount': lend_result[0], 'out_token': currency, 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp deposit https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["draw_cdp", "/kava.cdp.v1beta1.MsgDrawDebt", "/kava.hard.v1beta1.MsgBorrow"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'executed_at': timestamp, 'type': 'borrow', 'in_token': currency, 'in_amount': amount, 'out_token': f'borrow{currency}', 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'cdp draw https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_borrow_balance_sheet(currency, amount)
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["withdraw_cdp", "/kava.cdp.v1beta1.MsgWithdraw"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        lend_result = balance_sheet.put_lend_balance_sheet(currency, -amount)
        results.append({'executed_at': timestamp, 'type': 'recover', 'in_token': currency, 'in_amount': lend_result[0], 'out_token': f'lend{currency}', 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp withdraw https://www.mintscan.io/kava/txs/{txhash}'})
        if lend_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': lend_result[1], 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'lend interest https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["repay_cdp", "/kava.cdp.v1beta1.MsgRepayDebt"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        if len(amounts) not in [1, 2]:
          raise ValueError("not two amounts")
        for amount in amounts:
          amount, currency = split_amount(amount["value"])
          if action in ["repay_cdp", "/kava.cdp.v1beta1.MsgRepayDebt"] and currency.lower() == "usdx":
            borrow_result = balance_sheet.put_borrow_balance_sheet(currency, -amount)
            results.append({'executed_at': timestamp, 'type': 'repay', 'in_token': f'borrow{currency}', 'in_amount': borrow_result[0], 'out_token': currency, 'out_amount': borrow_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
            if borrow_result[1] != Decimal("0.0"):
              results.append({'executed_at': timestamp, 'type': 'pay', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': borrow_result[1], 'market_value': None, 'tags': None, 'comment': f'borrow interest https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet("KAVA", -fee)
          else:
            lend_result = balance_sheet.put_lend_balance_sheet(currency, -amount)
            results.append({'executed_at': timestamp, 'type': 'recover', 'in_token': currency, 'in_amount': lend_result[0], 'out_token': f'lend{currency}', 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
            if lend_result[1] != Decimal("0.0"):
              results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': lend_result[1], 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'lend interest https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["/kava.hard.v1beta1.MsgRepay"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        borrow_result = balance_sheet.put_borrow_balance_sheet(currency, -amount)
        results.append({'executed_at': timestamp, 'type': 'repay', 'in_token': f'borrow{currency}', 'in_amount': borrow_result[0], 'out_token': currency, 'out_amount': borrow_result[0], 'market_value': None, 'tags': None, 'comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
        if borrow_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'PAY', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': borrow_result[1], 'market_value': None, 'tags': None, 'comment': f'borrow interest https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["harvest_deposit", "hard_deposit", "/kava.hard.v1beta1.MsgDeposit"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'executed_at': timestamp, 'type': 'lend', 'in_token': f'lend{currency}', 'in_amount': amount, 'out_token': currency, 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'hard deposit https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_lend_balance_sheet(currency, amount)
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["harvest_withdraw", "hard_withdraw", "/kava.hard.v1beta1.MsgWithdraw"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        lend_result = balance_sheet.put_lend_balance_sheet(currency, -amount)
        results.append({'executed_at': timestamp, 'type': 'recover', 'in_token': currency, 'in_amount': lend_result[0], 'out_token': f'lend{currency}', 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'hard withdraw https://www.mintscan.io/kava/txs/{txhash}'})
        if lend_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': lend_result[1], 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'lend interest https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["claim_harvest_reward", "claim_reward", "withdraw_delegator_reward", "claim_hard_reward", "claim_usdx_minting_reward", "claim_delegator_reward", "/kava.incentive.v1beta1.MsgClaimHardReward", "/kava.incentive.v1beta1.MsgClaimDelegatorReward", "/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts_attribute = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        for amount_attribute in amounts_attribute:
          amounts = amount_attribute["value"].split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, amount)
        set_fee(fee, results, timestamp, txhash)
      elif action in ["vote"]:
        if fee != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'pay', 'in_token': None, 'in_amount': None, 'out_token': 'KAVA', 'out_amount': fee, 'market_value': None, 'tags': None, 'comment': f'create atomic swap https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action in ["delegate", "/cosmos.staking.v1beta1.MsgDelegate"]:
        delegate_event = get_event(raw_log["events"], "delegate")
        amount = get_attribute(delegate_event["attributes"], "amount")["value"]
        if action == "/cosmos.staking.v1beta1.MsgDelegate":
          amount, currency = split_amount(amount)
        else:
          amount = Decimal(amount) / Decimal("1000000")
        results.append({'executed_at': timestamp, 'type': 'lend', 'in_token': 'lendKAVA', 'in_amount': amount, 'out_token': 'KAVA', 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'delegate https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_lend_balance_sheet("KAVA", amount)
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
        transfer_event = list(filter(lambda x: x["type"] == "transfer", raw_log["events"]))
        if len(transfer_event) == 1:
          amount_attribute = list(filter(lambda x: x["key"] == "amount", transfer_event[0]["attributes"]))[0]["value"]
          amounts = amount_attribute.split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, amount)
        elif len(transfer_event) != 0:
          raise ValueError("too many transfer events")
      elif action in ["swap_exact_for_tokens", "/kava.swap.v1beta1.MsgSwapExactForTokens"]:
        swap_event = get_event(raw_log["events"], "swap_trade")

        input_amount = get_attribute(swap_event["attributes"], "input")["value"]
        input_amount, input_currency = split_amount(input_amount)
        output_amount = get_attribute(swap_event["attributes"], "output")["value"]
        output_amount, output_currency = split_amount(output_amount)
        exact = get_attribute(swap_event["attributes"], "exact")["value"]
        if exact == 'input':
          results.append({'executed_at': timestamp, 'type': "trade", 'in_token': input_currency, 'in_amount': input_amount, 'out_token': output_currency, 'out_amount': output_amount, 'market_value': None, 'tags': None, 'comment': f'swap https://www.mintscan.io/kava/txs/{txhash}'})
        elif exact == 'output':
          results.append({'executed_at': timestamp, 'type': "trade", 'in_token': input_currency, 'in_amount': input_amount, 'out_token': output_currency, 'out_amount': output_amount, 'market_value': None, 'tags': None, 'comment': f'swap https://www.mintscan.io/kava/txs/{txhash}'})

        balance_sheet.put_spot_balance_sheet(input_currency, - input_amount)
        balance_sheet.put_spot_balance_sheet(output_currency, output_amount)
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)

        fee_amount = get_attribute(swap_event["attributes"], "fee")["value"]
        amount, currency = split_amount(fee_amount)
        if amount != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'pay', 'in_token': None, 'in_amount': None, 'out_token': currency, 'out_amount': amount, 'market_value': None, 'tags': None, 'comment': f'swap fee https://www.mintscan.io/kava/txs/{txhash}'})
          balance_sheet.put_spot_balance_sheet(currency, - amount)
      elif action in ["begin_unbonding", "/cosmos.staking.v1beta1.MsgUndelegate"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        reward_amount = transfer_event["attributes"][2]["value"]
        reward_amount, reward_currency = split_amount(reward_amount)
        results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': reward_currency, 'in_amount': reward_amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'delegate reward https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet(reward_currency, reward_amount)

        unbond_event = get_event(raw_log["events"], "unbond")
        unbond_amount = unbond_event["attributes"][1]["value"].replace("ukava", "") + "ukava"
        unbond_amount, unbond_currency = split_amount(unbond_amount)
        lend_result = balance_sheet.put_lend_balance_sheet("KAVA", -unbond_amount)
        results.append({'executed_at': timestamp, 'type': 'recover', 'in_token': 'KAVA', 'in_amount': lend_result[0], 'out_token': 'lendKAVA', 'out_amount': lend_result[0], 'market_value': None, 'tags': None, 'comment': f'undelegate https://www.mintscan.io/kava/txs/{txhash}'})
        if lend_result[1] != Decimal("0.0"):
          results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': "KAVA", 'in_amount': lend_result[1], 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'lend interest https://www.mintscan.io/kava/txs/{txhash}'})
        balance_sheet.put_spot_balance_sheet("KAVA", -fee)
      elif action == "/cosmos.staking.v1beta1.MsgBeginRedelegate":
        transfer_event = list(filter(lambda x: x["type"] == "transfer", raw_log["events"]))
        if len(transfer_event) == 1:
          amount_attribute = get_attribute(transfer_event[0]["attributes"], "amount")["value"]
          amounts = amount_attribute.split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'executed_at': timestamp, 'type': 'obtain', 'in_token': currency, 'in_amount': amount, 'out_token': None, 'out_amount': None, 'market_value': None, 'tags': None, 'comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
            balance_sheet.put_spot_balance_sheet(currency, amount)
        elif len(transfer_event) != 0:
          raise ValueError("too many transfer events")
      else:
        raise ValueError(f"undefined action {action}")

  df = pd.DataFrame(results)
  df = df.sort_values('executed_at')
  #logger.debug(df)
  result_file_name = 'kava_settler_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['executed_at', 'type', 'in_token', 'in_amount', 'out_token', 'out_amount', 'market_value', 'tags', 'comment'])


def main():
  addresses = get_wallet_address()
  for address in addresses:
    create_cryptact_csv(address)


if __name__== '__main__':
  set_root_logger()
  main()
