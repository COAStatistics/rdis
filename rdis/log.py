import logging


class SimpleLog(object):

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        fmt = '[%(asctime)s] - %(levelname)s : %(message)s'
        formatter = logging.Formatter(fmt)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
#         log_file = './log.log'
#         file_handler = logging.FileHandler(log_file, encoding='utf8')
#         file_handler.setFormatter(formatter)
#         self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, level, msg):
        self.logger.log(level, msg)

    def set_level(self, level):
        self.logger.setLevel(level)

    @staticmethod
    def disable():
        logging.disable(50)


log = SimpleLog()
log.set_level(20)