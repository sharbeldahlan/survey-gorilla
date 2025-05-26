""" Common logging module for the apps. """
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance for the given module name.

    Ensures consistent formatting and output stream across the project.
    Attaches a StreamHandler to stdout if no handlers are already present.
    The logger is set to INFO level by default.

    Args:
        name (str): The name of the logger, typically __name__ of the module.

    Returns:
        logging.Logger: A logger configured with formatter and stdout handler.

    Note:
        Logging configuration should typically be initialized once at entry-point.
        This helper is safe to reuse across modules without adding duplicate handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
