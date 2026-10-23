import sys
from loguru import logger as loguru_logger
from pathlib import Path

def setup_logger(name: str, log_level: str = "INFO", log_file: Path = None):
    """
    Set up a logger with loguru.
    :param name: Logger name (used for identification).
    :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    :param log_file: Path to log file. If None, logs only to stderr.
    :return: Configured logger instance.
    """
    # Remove default handler
    loguru_logger.remove()
    # Add stderr handler
    loguru_logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    # Add file handler if log_file provided
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        loguru_logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="10 days",
            compression="zip"
        )
    # Return a logger bound to the name (optional)
    return loguru_logger.bind(name=name)