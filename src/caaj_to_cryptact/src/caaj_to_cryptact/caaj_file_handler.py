from caaj_to_cryptact.caaj_line import *
import logging
import csv

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())

class CaajFileHandler:
  @classmethod
  def get_caaj_lines(self, path):
    caaj_lines = []
    with open(path) as f:
      reader = csv.reader(f)
      header = next(reader)
      for line in reader:
        caaj_lines.append(CaajLine(line))

    return caaj_lines

