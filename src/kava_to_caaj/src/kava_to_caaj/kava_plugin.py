import logging
from caaj_plugin.caaj_plugin import *
from kava_to_caaj.transaction import *
from kava_to_caaj.message import *
from kava_to_caaj.message_factory import *
from decimal import *
from datetime import datetime as dt

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class KavaPlugin(CaajPlugin):
  PLATFORM = 'kava'
  def can_handle(self, transaction):
    try:
      chain_id = transaction['header']['chain_id']
      if 'kava' in chain_id:
        return True
      else:
        return False
    except Exception as e:
      return False

    return True

  def get_caajs(self, transaction_json:json, subject_address:str):
    caajs = []
    transaction = Transaction(transaction_json)
    logger.info(json.dumps(transaction.get_transaction_id()))
    messages = MessageFactory.get_messages(transaction_json) if transaction.get_fail() == False else []

    for message in messages:
      try:
        result = message.get_result()
        logger.debug(result)
      except Exception as e:
        logger.info('message.get_result() is failed. transaction:')        
        logger.info(json.dumps(transaction.transaction))
        raise e
      if result['action'] == 'delegate':
        caajs.extend(KavaPlugin.__as_delegate(transaction, result['result'], subject_address))
      elif result['action'] == 'begin_redelegate':
        caajs.extend(KavaPlugin.__as_delegate(transaction, result['result'], subject_address))
      elif result['action'] == 'begin_unbonding':
        caajs.extend(KavaPlugin.__as_begin_unbonding(transaction, result['result'], subject_address))
      elif result['action'] == 'send':
        caajs.extend(KavaPlugin.__as_send(transaction, result['result'], subject_address))
      elif result['action'] == 'deposit_within_batch':
        caajs.extend(KavaPlugin.__as_deposit_within_batch(transaction, result['result'], subject_address))
      elif result['action'] == 'withdraw_within_batch':
        caajs.extend(KavaPlugin.__as_withdraw_within_batch(transaction, result['result'], subject_address))
      elif result['action'] == 'hard_deposit':
        caajs.extend(KavaPlugin.__as_hard_deposit(transaction, result['result'], subject_address))
      elif result['action'] == 'hard_withdraw':
        caajs.extend(KavaPlugin.__as_hard_withdraw(transaction, result['result'], subject_address))
      elif result['action'] == 'hard_borrow':
        caajs.extend(KavaPlugin.__as_hard_borrow(transaction, result['result'], subject_address))
      elif result['action'] == 'hard_repay':
        caajs.extend(KavaPlugin.__as_hard_repay(transaction, result['result'], subject_address))
      elif result['action'] == 'claim_hard_reward':
        caajs.extend(KavaPlugin.__as_claim_hard_reward(transaction, result['result'], subject_address))
      elif result['action'] == 'create_cdp':
        caajs.extend(KavaPlugin.__as_create_cdp(transaction, result['result'], subject_address))
      elif result['action'] == 'draw_cdp':
        caajs.extend(KavaPlugin.__as_draw_cdp(transaction, result['result'], subject_address))
      elif result['action'] == 'repay_cdp':
        caajs.extend(KavaPlugin.__as_repay_cdp(transaction, result['result'], subject_address))
      elif result['action'] == 'deposit_cdp':
        caajs.extend(KavaPlugin.__as_deposit_cdp(transaction, result['result'], subject_address))
      elif result['action'] == 'withdraw_cdp':
        caajs.extend(KavaPlugin.__as_withdraw_cdp(transaction, result['result'], subject_address))
      elif result['action'] == 'claim_usdx_minting_reward':
        caajs.extend(KavaPlugin.__as_claim_usdx_minting_reward(transaction, result['result'], subject_address))
      elif result['action'] == 'createAtomicSwap' or result['action'] == 'claimAtomicSwap':
        caajs.extend(KavaPlugin.__as_createAtomicSwap(transaction, result['result'], subject_address))
      elif result['action'] == 'swap_exact_for_tokens':
        caajs.extend(KavaPlugin.__as_swap_exact_for_tokens(transaction, result['result'], subject_address))
      elif result['action'] == 'swap_deposit':
        caajs.extend(KavaPlugin.__as_swap_deposit(transaction, result['result'], subject_address))
      elif result['action'] == 'swap_withdraw':
        caajs.extend(KavaPlugin.__as_swap_withdraw(transaction, result['result'], subject_address))
      elif result['action'] == 'claim_swap_reward':
        caajs.extend(KavaPlugin.__as_claim_swap_reward(transaction, result['result'], subject_address))
      elif result['action'] == 'vote':
        pass
      else:
        logger.error(json.dumps('undefined action in KavaPlugin'))
        logger.error(json.dumps(transaction.transaction))

    fee = transaction.get_fee()
    caajs.extend(KavaPlugin.__as_transaction_fee(transaction, fee, subject_address))
    return caajs

  @classmethod
  def __as_transaction_fee(cls, transaction: Transaction, amount: str, subject_address: str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'FEE',
      'debit_amount':   {'KAVA': amount},
      'debit_from':     'kava_fee',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {'KAVA': amount},
      'credit_from':    subject_address,
      'credit_to':      'kava_fee',
      'comment':        f'transaction fee {amount} KAVA'
    }]
    return caajs

  @classmethod
  def __as_delegate(cls, transacton: Transaction, result, subject_address: str):
    caajs = []
    if result['staking_amount'] != None and Decimal(result['staking_amount']) != Decimal('0'):
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'STAKING',
        'debit_amount':   {result['staking_coin']: result['staking_amount']},
        'debit_from':     'kava_validator',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['staking_coin']: result['staking_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_validator',
        'comment':        f'staking {result["staking_amount"]} {result["staking_coin"]}'
      })
    # try to find delegate reward
    for reward in result['reward']:
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {reward['reward_coin']: reward['reward_amount']},
        'debit_from':     'kava_staking_reward',
        'debit_to':       subject_address,
        'credit_title':   'STAKINGREWARD',
        'credit_amount':  {reward['reward_coin']: reward['reward_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_staking_reward',
        'comment':        f'staking reward {reward["reward_amount"]} {reward["reward_coin"]}'
      })
    return caajs

  @classmethod
  def __as_begin_unbonding(cls, transacton: Transaction, result, subject_address: str):
    caajs = [{
      'time':           transacton.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transacton.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['unbonding_coin']: result['unbonding_amount']},
      'debit_from':     'kava_validator',
      'debit_to':       subject_address,
      'credit_title':   'STAKING',
      'credit_amount':  {result['unbonding_coin']: result['unbonding_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_validator',
      'comment':        f'unstaking {result["unbonding_amount"]} {result["unbonding_coin"]}'
    }]
    # try to find delegate reward
    for reward in result['reward']:
      caajs.append({
        'time':           transacton.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transacton.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {reward['reward_coin']: reward['reward_amount']},
        'debit_from':     'kava_staking_reward',
        'debit_to':       subject_address,
        'credit_title':   'STAKINGREWARD',
        'credit_amount':  {reward['reward_coin']: reward['reward_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_staking_reward',
        'comment':        f'staking reward {reward["reward_amount"]} {reward["reward_coin"]}'
      })
    return caajs

  @classmethod
  def __as_send(cls, transaction:Transaction, result, subject_address:str):
    recipient = result['recipient']
    sender = result['sender']

    if subject_address not in [recipient, sender]:
      caajs = []
    elif subject_address == recipient:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     sender,
        'debit_to':       recipient,
        'credit_title':   'RECEIVE',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    recipient,
        'credit_to':      sender,
        'comment':        f'{recipient} receive {result["amount"]} {result["coin"]} from {sender}'
      }]
    elif subject_address == sender:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SEND',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     recipient,
        'debit_to':       sender,
        'credit_title':   'SPOT',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    sender,
        'credit_to':      recipient,
        'comment':        f'{sender} send {result["amount"]} {result["coin"]} to {recipient}'
      }]

    return caajs

  @classmethod
  def __as_deposit_within_batch(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LIQUIDITY',
      'debit_amount':   {result['pool_coin']: result['pool_amount']},
      'debit_from':     'kava_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  result['liquidity_coin'],
      'credit_from':    subject_address,
      'credit_to':      'kava_liquidity',
      'comment':        f'deposit liquidity send {result["liquidity_coin"]} receive {result["pool_amount"]} {result["pool_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_withdraw_within_batch(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   result['liquidity_coin'],
      'debit_from':     'kava_liquidity',
      'debit_to':       subject_address,
      'credit_title':   'LIQUIDITY',
      'credit_amount':  {result['pool_coin']: result['pool_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_liquidity',
      'comment':        f'withdraw liquidity send {result["pool_amount"]} {result["pool_coin"]} receive {result["liquidity_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_hard_deposit(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LEND',
      'debit_amount':   {result['hard_deposit_coin']: result['hard_deposit_amount']},
      'debit_from':     'hard_lending',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {result['hard_deposit_coin']: result['hard_deposit_amount']},
      'credit_from':    subject_address,
      'credit_to':      'hard_lending',
      'comment':        f'hard deposit {result["hard_deposit_amount"]} {result["hard_deposit_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_hard_withdraw(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['hard_withdraw_coin']: result['hard_withdraw_amount']},
      'debit_from':     'hard_lending',
      'debit_to':       subject_address,
      'credit_title':   'LEND',
      'credit_amount':  {result['hard_withdraw_coin']: result['hard_withdraw_amount']},
      'credit_from':    subject_address,
      'credit_to':      'hard_lending',
      'comment':        f'hard withdraw {result["hard_withdraw_amount"]} {result["hard_withdraw_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_hard_borrow(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['hard_borrow_coin']: result['hard_borrow_amount']},
      'debit_from':     'hard_lending',
      'debit_to':       subject_address,
      'credit_title':   'BORROW',
      'credit_amount':  {result['hard_borrow_coin']: result['hard_borrow_amount']},
      'credit_from':    subject_address,
      'credit_to':      'hard_lending',
      'comment':        f'hard borrow {result["hard_borrow_amount"]} {result["hard_borrow_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_hard_repay(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'BORROW',
      'debit_amount':   {result['hard_repay_coin']: result['hard_repay_amount']},
      'debit_from':     'hard_lending',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {result['hard_repay_coin']: result['hard_repay_amount']},
      'credit_from':    subject_address,
      'credit_to':      'hard_lending',
      'comment':        f'hard repay {result["hard_repay_amount"]} {result["hard_repay_coin"]}'
    }]    
    return caajs

  @classmethod
  def __as_claim_hard_reward(cls, transaction:Transaction, result, subject_address:str):
    caajs = []
    for reward in result['reward']:
      caajs.append({
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {reward['reward_coin']: reward['reward_amount']},
        'debit_from':     'hard_lending',
        'debit_to':       subject_address,
        'credit_title':   'LENDINGREWARD',
        'credit_amount':  {reward['reward_coin']: reward['reward_amount']},
        'credit_from':    subject_address,
        'credit_to':      'hard_lending',
        'comment':        f'hard lending reward receive {reward["reward_amount"]} {reward["reward_coin"]}'
      })
    return caajs

  @classmethod
  def __as_create_cdp(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LEND',
      'debit_amount':   {result['deposit_coin']: result['deposit_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {result['deposit_coin']: result['deposit_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp deposit {result["deposit_amount"]} {result["deposit_coin"]}'
    },
    {
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['draw_coin']: result['draw_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'BORROW',
      'credit_amount':  {result['draw_coin']: result['draw_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp draw {result["draw_amount"]} {result["draw_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_draw_cdp(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['draw_coin']: result['draw_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'BORROW',
      'credit_amount':  {result['draw_coin']: result['draw_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp draw {result["draw_amount"]} {result["draw_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_repay_cdp(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'BORROW',
      'debit_amount':   {result['repay_coin']: result['repay_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {result['repay_coin']: result['repay_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp repay {result["repay_amount"]} {result["repay_coin"]}'
    }]

    if result['withdraw_coin'] != None and result['withdraw_amount'] != None:
      caajs.append({
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['withdraw_coin']: result['withdraw_amount']},
        'debit_from':     'kava_cdp',
        'debit_to':       subject_address,
        'credit_title':   'LEND',
        'credit_amount':  {result['withdraw_coin']: result['withdraw_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_cdp',
        'comment':        f'cdp withdraw {result["withdraw_amount"]} {result["withdraw_coin"]}'
      })

    return caajs

  @classmethod
  def __as_deposit_cdp(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LEND',
      'debit_amount':   {result['deposit_coin']: result['deposit_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  {result['deposit_coin']: result['deposit_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp deposit {result["deposit_amount"]} {result["deposit_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_withdraw_cdp(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['withdraw_coin']: result['withdraw_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'LEND',
      'credit_amount':  {result['withdraw_coin']: result['withdraw_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp withdraw {result["withdraw_amount"]} {result["withdraw_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_claim_usdx_minting_reward(cls, transaction:Transaction, result, subject_address:str):
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   {result['reward'][0]['reward_coin']: result['reward'][0]['reward_amount']},
      'debit_from':     'kava_cdp',
      'debit_to':       subject_address,
      'credit_title':   'LENDINGREWARD',
      'credit_amount':  {result['reward'][0]['reward_coin']: result['reward'][0]['reward_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_cdp',
      'comment':        f'cdp reward {result["reward"][0]["reward_amount"]} {result["reward"][0]["reward_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_createAtomicSwap(cls, transaction:Transaction, result, subject_address:str):
    recipient = result['recipient']
    sender = result['sender']

    if subject_address not in [recipient, sender]:
      caajs = []
    elif subject_address == recipient:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     'kava_bc_atomic_swap',
        'debit_to':       subject_address,
        'credit_title':   'RECEIVE',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_bc_atomic_swap',
        'comment':        f'{subject_address} receive {result["amount"]} {result["coin"]} from kava_bc_atomic_swap'
      }]
    elif subject_address == sender:
      caajs = [{
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SEND',
        'debit_amount':   {result['coin']: result['amount']},
        'debit_from':     'kava_bc_atomic_swap',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['coin']: result['amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_bc_atomic_swap',
        'comment':        f'{subject_address} send {result["amount"]} {result["coin"]} to kava_bc_atomic_swap'
      }]

    return caajs

  @classmethod
  def __as_swap_exact_for_tokens(cls, transaction:Transaction, result, subject_address:str):
    caajs = []
    if not (Decimal(result['input_amount']) == Decimal('0') and Decimal(result['output_amount']) == Decimal('0')):
      caajs.extend([{
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'SPOT',
        'debit_amount':   {result['output_coin']: result['output_amount']},
        'debit_from':     'kava_swap',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['input_coin']: result['input_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_swap',
        'comment':        f'buy {result["output_amount"]} {result["output_coin"]} sell {result["input_amount"]} {result["input_coin"]}'
      },
      {
        'time':           transaction.get_time(),
        'platform':       KavaPlugin.PLATFORM,
        'transaction_id': transaction.get_transaction_id(),
        'debit_title':    'FEE',
        'debit_amount':   {result['fee_coin']: result['fee_amount']},
        'debit_from':     'kava_swap',
        'debit_to':       subject_address,
        'credit_title':   'SPOT',
        'credit_amount':  {result['fee_coin']: result['fee_amount']},
        'credit_from':    subject_address,
        'credit_to':      'kava_swap',
        'comment':        f'pay {result["fee_amount"]} {result["fee_coin"]} as swap fee'
      }])
  
    return caajs

  @classmethod
  def __as_swap_deposit(cls, transaction:Transaction, result, subject_address:str):
    input_amount = {}
    for x in result['inputs']:
      input_amount[x['input_coin']] = x['input_amount'] 
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'LIQUIDITY',
      'debit_amount':   {result['share_coin']: result['share_amount']},
      'debit_from':     'kava_swap',
      'debit_to':       subject_address,
      'credit_title':   'SPOT',
      'credit_amount':  input_amount,
      'credit_from':    subject_address,
      'credit_to':      'kava_swap',
      'comment':        f'kava swap send {input_amount} receive {result["share_amount"]} {result["share_coin"]}'
    }]

    return caajs

  @classmethod
  def __as_swap_withdraw(cls, transaction:Transaction, result, subject_address:str):
    output_amount = {}
    for x in result['outputs']:
      output_amount[x['output_coin']] = x['output_amount'] 
    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   output_amount,
      'debit_from':     'kava_swap',
      'debit_to':       subject_address,
      'credit_title':   'LIQUIDITY',
      'credit_amount':  {result['share_coin']: result['share_amount']},
      'credit_from':    subject_address,
      'credit_to':      'kava_swap',
      'comment':        f'kava swap send {result["share_amount"]} {result["share_coin"]} receive {output_amount}'
    }]

    return caajs

  @classmethod
  def __as_claim_swap_reward(cls, transaction:Transaction, result, subject_address:str):
    reward_amount = {}
    for x in result['rewards']:
      reward_amount[x['reward_coin']] = x['reward_amount'] 

    caajs = [{
      'time':           transaction.get_time(),
      'platform':       KavaPlugin.PLATFORM,
      'transaction_id': transaction.get_transaction_id(),
      'debit_title':    'SPOT',
      'debit_amount':   reward_amount,
      'debit_from':     'kava_swap',
      'debit_to':       subject_address,
      'credit_title':   'LIQUIDITYREWARD',
      'credit_amount':  reward_amount,
      'credit_from':    subject_address,
      'credit_to':      'kava_swap',
      'comment':        f'kava swap reward {reward_amount}'
    }]

    return caajs