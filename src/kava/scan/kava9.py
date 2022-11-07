from .base import KavaBase

class Kava9(KavaBase):
  def cdp_tracking(self,cdp_trucker, transaction, fee, timestamp):
    results = []
    tx_msg = transaction['data']['tx']['body']['messages'][0]
    action = tx_msg['@type']
    txhash = transaction['data']['txhash']
    events = transaction['data']['logs'][0]['events']
    return self.devide_action(cdp_trucker, fee, timestamp,tx_msg,action,txhash,events)
