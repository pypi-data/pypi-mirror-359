import logging.config
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()

format_str = '%(message)%(levelname)%(name)%(asctime)'
formatter = jsonlogger.JsonFormatter(format_str)
handler.setFormatter(formatter)
log = logging.getLogger()
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False

class JsonLogger:
    def __init__(self, log: logging.Logger):
        self.log = log

    def info(self, message: str):
        self.log.info(message, extra={'level': 'INFO'})

    def warning(self, message: str, warning: str = ""):
        self.log.warning(message, extra={'level': 'WARNING'})

    def error(self, message: str, error: str = ""):
        self.log.error(message, extra={'level': 'ERROR'})


logger = JsonLogger(log)
info = logger.info
warning = logger.warning
error = logger.error
