"""
Logging utilities for the data pipeline.
Provides a consistent logging format and helper to configure loggers.
"""
import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with standard formatting.
    
    Args:
        name: The name of the logger (usually __name__).
    
    Returns:
        A configured logging.Logger instance.
    """
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        log.addHandler(handler)
        log.setLevel(logging.INFO)
    return log
