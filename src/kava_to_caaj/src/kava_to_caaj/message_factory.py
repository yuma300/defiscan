from decimal import *
import logging
from kava_to_caaj.message import *

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class MessageFactory:
  @classmethod
  def get_messages(cls, transaction:json)->list:
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