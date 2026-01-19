import logging
import os

class HelwanLogger:
    def __init__(self, log_file="hel-stream.log"):
        self.log_path = os.path.join(os.path.expanduser("~"), log_file)
        
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("HelwanStream")

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)
