import logging

class Logger:
    formatter       = logging.Formatter('[%(name)s.%(funcName)s: %(levelname)s] %(message)s')
    handler         = logging.StreamHandler()
    handler.setFormatter(formatter)

    def __init__(self, loggerName: str) -> None:
        self.log = logging.getLogger(loggerName)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger = Logger("test")
    logger.log.debug("debug message")
    logger.log.info("info message")
    logger.log.warning("warning message")
    logger.log.error("error message")
