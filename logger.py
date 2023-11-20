import logging

class Logger:
    FATAL           = logging.FATAL
    ERROR           = logging.ERROR
    WARNING         = logging.WARNING
    WARN            = logging.WARN
    INFO            = logging.INFO
    DEBUG           = logging.DEBUG
    NOTSET          = logging.NOTSET

    formatter       = logging.Formatter('[%(name)s->%(filename)s->%(funcName)s: %(levelname)s] %(message)s')
    handler         = logging.StreamHandler()
    handler.setFormatter(formatter)

    def __init__(self, loggerName: str) -> None:
        self.log = logging.getLogger(loggerName)
        self.log.addHandler(self.handler)
        self.log.setLevel(self.DEBUG)