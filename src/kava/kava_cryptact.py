import sys
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt
import datetime
import re
import os
import logging
import re
from typing import Union


logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

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

# def split_amount(value:str)->tuple(int,str):
def split_amount(value:str)-> Union[Decimal, str]:
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

  cdp_trucker = []
  #logger.debug(address)
  for transaction in transactions:
    #transaction = json.loads(transaction)
    #logger.debug(transaction)
    logger.debug(json.dumps(transaction['header'], indent=2))
    #logger.debug(json.dumps(transaction, indent=2))
    chain_id = transaction['header']['chain_id']
    timestamp = dt.strptime(transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    timestamp = timestamp.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    timestamp = datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    txhash = transaction['data']['txhash']
    fee = 0
    raw_logs = json.loads(transaction['data']['raw_log'])
    for raw_log in raw_logs:
      message_event = get_event(raw_log["events"], "message")
      action = get_attribute(message_event["attributes"], "action")["value"]
      if action in ["send", "/cosmos.bank.v1beta1.MsgSend"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        sender_address = get_attribute(transfer_event["attributes"], "sender")["value"]
        receiver_address = get_attribute(transfer_event["attributes"], "recipient")["value"]
        if sender_address == receiver_address:
          results.append({'Timestamp': timestamp, 'Action': 'SENDFEE', 'Source': 'kava', 'Source': 'kava', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'self transfer https://www.mintscan.io/kava/txs/{txhash}'})
        elif sender_address == address:
          results.append({'Timestamp': timestamp, 'Action': 'CONFIRM', 'Source': 'kava', 'Base': currency, 'Volume': - amount, 'Price': 0, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'send https://www.mintscan.io/kava/txs/{txhash}'})
        elif receiver_address == address:
          results.append({'Timestamp': timestamp, 'Action': 'CONFIRM', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': 0, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'receive https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["create_cdp", "/kava.cdp.v1beta1.MsgCreateCDP"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        if len(amounts) != 2:
          raise ValueError("not two amounts")
        for amount in amounts:
          amount, currency = split_amount(amount["value"])
          if currency.lower() == "usdx":
            results.append({'Timestamp': timestamp, 'Action': 'BORROW', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp create https://www.mintscan.io/kava/txs/{txhash}'})
          else:
            results.append({'Timestamp': timestamp, 'Action': 'LEND', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'cdp create https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["deposit_cdp", "/kava.cdp.v1beta1.MsgDeposit"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'LEND', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp deposit https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["draw_cdp", "/kava.cdp.v1beta1.MsgDrawDebt", "/kava.hard.v1beta1.MsgBorrow"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'BORROW', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp draw https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["withdraw_cdp", "/kava.cdp.v1beta1.MsgWithdraw"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'RECOVER', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp withdraw https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["repay_cdp", "/kava.cdp.v1beta1.MsgRepayDebt"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        if len(amounts) not in [1, 2]:
          raise ValueError("not two amounts")
        for amount in amounts:
          amount, currency = split_amount(amount["value"])
          if action in ["repay_cdp", "/kava.cdp.v1beta1.MsgRepayDebt"] and currency.lower() == "usdx":
            results.append({'Timestamp': timestamp, 'Action': 'RETURN', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
          else:
            results.append({'Timestamp': timestamp, 'Action': 'RECOVER', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["/kava.hard.v1beta1.MsgRepay"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'RETURN', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'cdp repay https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["harvest_deposit", "hard_deposit", "/kava.hard.v1beta1.MsgDeposit"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'LEND', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'hard deposit https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["harvest_withdraw", "hard_withdraw", "/kava.hard.v1beta1.MsgWithdraw"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amount = get_attribute(transfer_event["attributes"], "amount")["value"]
        amount, currency = split_amount(amount)
        results.append({'Timestamp': timestamp, 'Action': 'RECOVER', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'hard withdraw https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["claim_harvest_reward", "claim_reward", "withdraw_delegator_reward", "claim_hard_reward", "claim_usdx_minting_reward", "claim_delegator_reward", "/kava.incentive.v1beta1.MsgClaimHardReward", "/kava.incentive.v1beta1.MsgClaimDelegatorReward", "/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        amounts_attribute = list(filter(lambda x: x["key"] == "amount", transfer_event["attributes"]))
        for amount_attribute in amounts_attribute:
          amounts = amount_attribute["value"].split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'Timestamp': timestamp, 'Action': 'BONUS', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["createAtomicSwap", "claimAtomicSwap", "/kava.bep3.v1beta1.MsgCreateAtomicSwap", "/kava.bep3.v1beta1.MsgClaimAtomicSwap", "vote"]:
        if fee != Decimal("0.0"):
          results.append({'Timestamp': timestamp, 'Action': 'SENDFEE', 'Source': 'kava', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'create atomic swap https://www.mintscan.io/kava/txs/{txhash}'})
      elif action == "refundAtomicSwap":
        pass
      elif action in ["delegate", "/cosmos.staking.v1beta1.MsgDelegate"]:
        delegate_event = get_event(raw_log["events"], "delegate")
        amount = get_attribute(delegate_event["attributes"], "amount")["value"]
        if action == "/cosmos.staking.v1beta1.MsgDelegate":
          amount, currency = split_amount(amount)
        else:
          amount = Decimal(amount) / Decimal("1000000")
        results.append({'Timestamp': timestamp, 'Action': 'LEND', 'Source': 'kava', 'Base': 'KAVA', 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'delegate https://www.mintscan.io/kava/txs/{txhash}'})
        transfer_event = list(filter(lambda x: x["type"] == "transfer", raw_log["events"]))
        if len(transfer_event) == 1:
          amount_attribute = list(filter(lambda x: x["key"] == "amount", transfer_event[0]["attributes"]))[0]["value"]
          amounts = amount_attribute.split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'Timestamp': timestamp, 'Action': 'BONUS', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
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
          price = input_amount / output_amount
          results.append({'Timestamp': timestamp, 'Action': "BUY", 'Source': 'kava', 'Base': output_currency, 'Volume': output_amount, 'Price': price, 'Counter': input_currency, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'swap https://www.mintscan.io/kava/txs/{txhash}'})
        elif exact == 'output':
          price = output_amount / input_amount
          results.append({'Timestamp': timestamp, 'Action': "SELL", 'Source': 'kava', 'Base': input_currency, 'Volume': input_amount, 'Price': price, 'Counter': output_currency, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'swap https://www.mintscan.io/kava/txs/{txhash}'})

        fee_amount = get_attribute(swap_event["attributes"], "fee")["value"]
        amount, currency = split_amount(fee_amount)
        if amount != Decimal("0.0"):
          results.append({'Timestamp': timestamp, 'Action': 'SENDFEE', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'swap fee https://www.mintscan.io/kava/txs/{txhash}'})
      elif action in ["begin_unbonding", "/cosmos.staking.v1beta1.MsgUndelegate"]:
        transfer_event = get_event(raw_log["events"], "transfer")
        if len(transfer_event["attributes"]) != 6:
          raise ValueError(f"invalid number of transfer attributes {transfer_event['attributes']}")
        reward_amount = transfer_event["attributes"][2]["value"]
        reward_amount, reward_currency = split_amount(reward_amount)
        results.append({'Timestamp': timestamp, 'Action': 'BONUS', 'Source': 'kava', 'Base': reward_currency, 'Volume': reward_amount, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': f'delegate reward https://www.mintscan.io/kava/txs/{txhash}'})

        unbond_amount = transfer_event["attributes"][5]["value"]
        unbond_amount, unbond_currency = split_amount(unbond_amount)
        results.append({'Timestamp': timestamp, 'Action': 'RECOVER', 'Source': 'kava', 'Base': 'KAVA', 'Volume': unbond_amount, 'Price': None, 'Counter': unbond_amount, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'undelegate https://www.mintscan.io/kava/txs/{txhash}'})
      elif action == "/cosmos.staking.v1beta1.MsgBeginRedelegate":
        transfer_event = list(filter(lambda x: x["type"] == "transfer", raw_log["events"]))
        if len(transfer_event) == 1:
          amount_attribute = get_attribute(transfer_event[0]["attributes"], "amount")["value"]
          amounts = amount_attribute.split(",")
          for amount in amounts:
            amount, currency = split_amount(amount)
            results.append({'Timestamp': timestamp, 'Action': 'BONUS', 'Source': 'kava', 'Base': currency, 'Volume': amount, 'Price': None, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': f'hard reward https://www.mintscan.io/kava/txs/{txhash}'})
        elif len(transfer_event) != 0:
          raise ValueError("too many transfer events")
      else:
        raise ValueError(f"undefined action {action}")

  df = pd.DataFrame(results)
  df = df.sort_values('Timestamp')
  #logger.debug(df)
  result_file_name = 'kava_cryptact_%s.csv' % address
  df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])


def main():
  addresses = get_wallet_address()
  for address in addresses:
    create_cryptact_csv(address)


if __name__== '__main__':
  set_root_logger()
  main()
