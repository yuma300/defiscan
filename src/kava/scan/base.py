import logging
from decimal import Decimal
import re

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())



# types on mintscan web      : types on mintscan api
# CDP Draw Debt              : draw_cdp
# CDP Deposit                : deposit_cdp
# CDP Repay Debt             : repay_cdp
# CDP Withdraw               : withdraw_cdp
# Claim Atomic Swap          : claimAtomicSwap
# Claim HARD LP Reward       : claim_hard_reward
# Claim USDX Minting Reward  : claim_usdx_minting_reward
# Create Atomic Swap         : createAtomicSwap
# Create CDP                 : create_cdp
# Delegate                   : delegate
# Get Reward                 : withdraw_delegator_reward
# HARD Deposit               : hard_deposit
# HARD Withdraw              : hard_withdraw
# Harvest Claim Reward       : claim_harvest_reward
# Harvest Deposit            : harvest_deposit
# Harvest Withdraw           : harvest_withdraw
# MsgClaimReward             : claim_reward
# Refund Atomic Swap         : refundAtomicSwap
# Send                       : send
# Undelegate                 : begin_unbonding
# Vote                       : vote
# HARD Withdraw              : hard_borrow
# HARD Repay                 : hard_repay
# Deposit                    : swap_deposit
# Withdraw                   : swap_withdraw
# Claim Swap Reward          : claim_swap_reward
# Comitty Vote               : committee_vote


class KavaBase():
  def kava_version():
    array = []
    for i in range(1,10):
      array.push(f"kava-{i}")
    array.push("kava_2222-10")
    return array
  def cdp_tracking(self,cdp_trucker, transaction, fee, timestamp):
    results = []
    tx_msg = transaction['data']['tx']['value']['msg'][0]
    action = tx_msg['type']
    txhash = transaction['data']['txhash']
    events = transaction['data']['logs'][0]['events']
    return self.devide_action(cdp_trucker, fee, timestamp,tx_msg,action,txhash,events)

  def devide_action(self,cdp_trucker, fee, timestamp,tx_msg,action,txhash,events):
    results = []
    if action == 'cdp/MsgCreateCDP':
      collateral_token = tx_msg['value']['collateral_type']
      cdp_list = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))
      if len(cdp_list) > 0: # check same collateral cdp already exist. if true, it means liquidation was executed.
        cdp = cdp_list[0]
        results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': cdp['debt_amount'], 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp liquidated https://www.mintscan.io/kava/txs/%s' % txhash})
        cdp_trucker.remove(cdp)

      collateral_amount = Decimal(tx_msg['value']['collateral']['amount']) / Decimal('100000000')
      debt_amount = Decimal(tx_msg['value']['principal']['amount'])/ Decimal('1000000')
      cdp = {'collateral_token': collateral_token, 'collateral_amount': collateral_amount, 'debt_amount': debt_amount}
      cdp_trucker.append(cdp)
      results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'BORROW', 'Base': 'USDX', 'Volume': debt_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp create https://www.mintscan.io/kava/txs/%s' % txhash})
    elif action == 'cdp/MsgDrawDebt':
      collateral_token = tx_msg['value']['collateral_type']
      debt_amount = Decimal(tx_msg['value']['principal']['amount'])/ Decimal('1000000')
      try:
        cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
        cdp['debt_amount'] += debt_amount
      except IndexError as e:
        logger.critical('cdp/MsgDrawDebt. CDP does not exist!!!!!!')
        raise e

      results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'BORROW', 'Base': 'USDX', 'Volume': debt_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp draw https://www.mintscan.io/kava/txs/%s' % txhash})
    elif action == 'cdp/MsgRepayDebt':
      collateral_token = tx_msg['value']['collateral_type']
      repay_amount = Decimal(tx_msg['value']['payment']['amount'])/ Decimal('1000000')
      try:
        cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
        if len(list(filter(lambda item: item['type'] == 'cdp_close', events))) != 0: # check wether close or not
          if cdp['debt_amount'] - repay_amount > 0: # check total debt amount is not bigger than total repayamount
            raise ValueError('%s: total debt amount (%s) is bigger than total repayment (%s).' % (collateral_token, cdp['debt_amount'], repay_amount))
          interest_amount = repay_amount - cdp['debt_amount'] # calcurate interest amount
          transfer_attributes = list(filter(lambda item: item['type'] == 'transfer', events))[0]['attributes']
          withdraw_amount = list(filter(lambda item: item['key'] == 'amount' and 'usdx' not in item['value'], transfer_attributes))[0]['value']
          withdraw_amount = Decimal(re.sub(r"\D", "", withdraw_amount))/ Decimal('100000000')

          if cdp['collateral_amount'] != withdraw_amount: # check withdraw amount is equal to collateral_amount
            raise ValueError('%s: collateral_amount is not equal to withdraw amount (%s)' % collateral_token, cdp['collateral_amount'], withdraw_amount)

          results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': cdp['debt_amount'], 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp close https://www.mintscan.io/kava/txs/%s' % txhash})
          results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SELL', 'Base': 'USDX', 'Volume': interest_amount, 'Price': 0, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'cdp repay interest https://www.mintscan.io/kava/txs/%s' % txhash})
          cdp_trucker.remove(cdp)
        else:
          if cdp['debt_amount'] - repay_amount < 0: # check total debt amount is bigger than total repayamount
            raise ValueError('%s: total debt amount is not bigger than total repayment.' % collateral_token)
          cdp['debt_amount'] -= repay_amount
          results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'RETURN', 'Base': 'USDX', 'Volume': repay_amount, 'Price': 110, 'Counter': 'JPY', 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'cdp repay https://www.mintscan.io/kava/txs/%s' % txhash})
      except IndexError as e:
        logger.critical('cdp/MsgRepayDebt. CDP does not exist!!!!!!')
        raise e
    elif action == 'cdp/MsgWithdraw':
      collateral_token = tx_msg['value']['collateral_type']
      collateral_amount = Decimal(tx_msg['value']['collateral']['amount'])/ Decimal('100000000')
      try:
        cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
        if cdp['collateral_amount'] - Decimal(collateral_amount) < 0: # check total withdraw amount is not bigger than collateral
          raise ValueError('%s: withdraw amount (%s) is bigger than collateral amount (%s).' % collateral_token, collateral_amount, cdp['collateral_amount'])
        cdp['collateral_amount'] -= Decimal(collateral_amount)
      except IndexError as e:
        logger.critical('cdp/MsgWithdraw. CDP does not exist!!!!!!')
        raise e

      if fee == 0: return results
      results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp https://www.mintscan.io/kava/txs/%s' % txhash})
    elif action == 'cdp/MsgDeposit':
      collateral_token = tx_msg['value']['collateral_type']
      collateral_amount = Decimal(tx_msg['value']['collateral']['amount'])/ Decimal('100000000')
      try:
        cdp = list(filter(lambda item: item['collateral_token'] == collateral_token, cdp_trucker))[0]
        cdp['collateral_amount'] += Decimal(collateral_amount)
      except IndexError as e:
        logger.critical('cdp/MsgDeposit. CDP does not exist!!!!!!')
        raise e

      if fee == 0: return results
      results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SENDFEE', 'Base': 'KAVA', 'Volume': fee, 'Price': None, 'Counter': 'JPY', 'Fee': 0, 'FeeCcy': 'KAVA', 'Comment': 'deposit cdp https://www.mintscan.io/kava/txs/%s' % txhash})
    elif action == 'swap/MsgSwapExactForTokens':
      pass
      # input_denominator = Decimal('1000000') if tx_msg['value']['exact_token_a']['denom'] != 'busd' else Decimal('100000000')
      # input_token = tx_msg['value']['exact_token_a']['denom'].upper()
      # input_amount = Decimal(tx_msg['value']['exact_token_a']['amount'])/ input_denominator
      # output_denominator = Decimal('1000000') if tx_msg['value']['token_b']['denom'] != 'busd' else Decimal('100000000')
      # output_token = tx_msg['value']['token_b']['denom'].upper()
      # output_amount = Decimal(tx_msg['value']['token_b']['amount'])/ output_denominator
      # price = output_amount / input_amount
      # results.append({'Timestamp': timestamp, 'Source': 'kava', 'Action': 'SELL', 'Base': input_token, 'Volume': input_amount, 'Price': price, 'Counter': output_token, 'Fee': fee, 'FeeCcy': 'KAVA', 'Comment': 'swap https://www.mintscan.io/kava/txs/%s' % txhash})

    #print(cdp_trucker)
    return results
