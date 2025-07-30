"""Logging utilities for modelhub-observability."""

import logging
import os
import sys
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """
    A custom log formatter with enhanced contextual information.

    This formatter adds timestamp, app label, file name, function name,
    and line number to each log record.
    """

    def format(self, record):
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        record.label = f"[{os.environ.get('APP_NAME', 'modelhub-obs')}]"

        # Add file location info
        record.file_info = f"{record.pathname.split('/')[-1]}:{record.lineno}"

        # Add function info if available
        if record.funcName and record.funcName != "<module>":
            record.file_info = f"{record.file_info} {record.funcName}()"

        return super().format(record)


def setup_logger(name):
    """
    Set up a logger with enhanced contextual information.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger object.
    """
    logger = logging.getLogger(name)

    # Set log level from environment variable
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)

    if not logger.hasHandlers():
        log_handler = logging.StreamHandler(sys.stdout)

        # Enhanced format with file location and function information
        formatter = CustomFormatter(
            fmt="%(timestamp)s %(label)s %(levelname)s [%(name)s] [%(file_info)s]: %(message)s"
        )

        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger
