import logging
import sys
from .config import Config
from threading import Lock


class Log:
    """
    Singleton logger class
    """

    __instance = None
    lock = Lock()

    def __init__(self):
        self.DEBUG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s \n[in %(pathname)s]'
        self.INFO_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'

    def _initialize(self):
        logger = logging.getLogger('kb')

        logger.setLevel(Config.LOG_LEVEL)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(
            logging.Formatter(self.INFO_FORMAT)
        )

        logger.addHandler(stream_handler)
        logger.propagate = False
        Log.lock = Lock()

        return logger

    @staticmethod
    def get_logger():
        """
            Logger singleton: ensures that there is only one instance of logger
                throughout the whole application
        :return: logger
        """
        if not Log.__instance:
            Log.__instance = Log()._initialize()
        return Log.__instance
