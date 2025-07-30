"""Utility module for logging configuration."""
import logging

def setup_logger(name):
    """Setup and return a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

__all__ = ["setup_logger"]
