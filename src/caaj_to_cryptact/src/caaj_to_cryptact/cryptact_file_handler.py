from decimal import *
import logging
import pandas as pd

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
getcontext().prec = 50

class CryptactFileHandler:
  @classmethod
  def write_cryptact_lines(cls, cryptact_lines:list):
    cryptact_json = list(map(lambda x: x.get_dict(), cryptact_lines))
    df = pd.DataFrame(cryptact_json)
    logger.debug(df)
    df = df.sort_values('Timestamp')
    result_file_name = 'cryptact.csv'
    df.to_csv(result_file_name, index=False, columns=['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment'])
