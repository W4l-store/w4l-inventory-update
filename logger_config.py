import os
import logging
from logging.handlers import RotatingFileHandler
from collections import deque
import time
from utils.helpers import a_ph, append_to_processing_logs

# Custom filter to prevent duplicate log messages within a specified time frame
class TimedDuplicateFilter(logging.Filter):
    def __init__(self, timeout=3600, max_cache=1000):
        super().__init__()
        self.msgs = deque(maxlen=max_cache)
        self.timeout = timeout

    def filter(self, record):
        msg = record.msg
        current_time = time.time()
        self.msgs = deque([(m, t) for m, t in self.msgs if current_time - t < self.timeout], maxlen=self.msgs.maxlen)
        if msg not in [m for m, _ in self.msgs]:
            self.msgs.append((msg, current_time))
            return True
        return False

# Custom handler to append logs to processing_logs
class ProcessingLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        append_to_processing_logs(log_entry)

# Function to set up the logger
def setup_logger():
    # Use the standard Logger class
    logging.setLoggerClass(logging.Logger)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # # Set up file logging
    # log_file = a_ph('app.log')
    # log_dir = os.path.dirname(log_file)
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)

    # file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    # file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)

    # Add timed duplicate filter
    timed_duplicate_filter = TimedDuplicateFilter(timeout=3600, max_cache=1000)
    # file_handler.addFilter(timed_duplicate_filter)

    # root_logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add custom ProcessingLogsHandler
    processing_logs_handler = ProcessingLogsHandler()
    processing_logs_handler.setLevel(logging.INFO)
    processing_logs_handler.setFormatter(formatter)
    root_logger.addHandler(processing_logs_handler)

    # Apply filter to all existing loggers
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.addFilter(timed_duplicate_filter)

    return root_logger

# Usage example (can be removed if not needed)
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("This is a test log message")
