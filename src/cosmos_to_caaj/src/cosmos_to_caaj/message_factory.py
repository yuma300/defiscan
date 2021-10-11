from decimal import *
import logging
from cosmos_to_caaj.message import *
from cosmos_to_caaj.message_v3 import *
from cosmos_to_caaj.message_v2 import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class MessageFactory:
  @classmethod
  def get_messages(cls, transaction:json)->list:
    if transaction['header']['chain_id'] == 'cosmoshub-4':
      try:
        log_events = list(map(lambda x: x['events'], transaction['data']['logs']))
      except Exception as e:
        logger.error("get_messages failed. can not get log_event transaction:")
        logger.error(json.dumps(transaction))     
        raise e
      messages_events = transaction['data']['tx']['body']['messages']
      messages = []
      for i, log_event in enumerate(log_events):
        messages.append(Message(log_event, messages_events[i], transaction['data']['height'], transaction['header']['chain_id']))
    elif transaction['header']['chain_id'] == 'cosmoshub-3':    
      try:
        log_events = list(map(lambda x: x['events'], transaction['data']['logs']))
      except Exception as e:
        logger.error("get_messages failed. can not get log_event transaction:")
        logger.error(json.dumps(transaction))     
        raise e
      messages_events = transaction['data']['tx']['value']['msg']
      messages = []
      for i, log_event in enumerate(log_events):
        messages.append(MessageV3(log_event, messages_events[i], transaction['data']['height'], transaction['header']['chain_id']))
    elif transaction['header']['chain_id'] == 'cosmoshub-2':    
      messages_events = transaction['data']['tx']['value']['msg']
      messages = []
      for i, messages_event in enumerate(messages_events):
        messages.append(MessageV2(messages_event, transaction['data']['tags'], transaction['data']['height'], transaction['header']['chain_id']))
    else:
      try:
        log_events = list(map(lambda x: x['events'], transaction['data']['logs']))
      except Exception as e:
        logger.error("get_messages failed. can not get log_event transaction:")
        logger.error(json.dumps(transaction))     
        raise e

      messages_events = transaction['data']['tx']['value']['msg']
      messages = []
      for i, log_event in enumerate(log_events):
        messages.append(Message(log_event, messages_events[i], transaction['data']['height'], transaction['header']['chain_id']))

    
    return messages