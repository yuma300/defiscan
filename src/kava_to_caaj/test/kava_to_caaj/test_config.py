import logging

class TestConfig:
  CRITICAL = logging.CRITICAL
  ERROR = logging.ERROR
  WARNING = logging.WARNING
  INFO = logging.INFO
  DEBUG = logging.DEBUG
  NOTEST = logging.NOTSET

  @classmethod
  def set_root_logger(cls, level):
    root_logger = logging.getLogger(name=None)
    root_logger.setLevel(level)
    if not root_logger.hasHandlers():
      fmt = logging.Formatter("%(asctime)s, %(name)s, %(lineno)s, %(levelname)s, %(message)s", "%Y-%m-%dT%H:%M:%S")
      stream_handler = logging.StreamHandler()
      stream_handler.setLevel(level)
      stream_handler.setFormatter(fmt)
      root_logger.addHandler(stream_handler)