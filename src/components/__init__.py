import logging

# Logger setup
def setup_logger() -> logging.Logger:
    """
    Configure and return application logger.

    Returns:
        Configured logger instance with console handler
    """
    logger = logging.getLogger("components")
    logger.setLevel(logging.INFO)

    # Add console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Initialize logger
logger = setup_logger()

# Exports
__all__ = ["logger"]
