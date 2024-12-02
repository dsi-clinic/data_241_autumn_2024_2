import logging

def setup_logging():
    """Set up and return a custom logger."""
    logger = logging.getLogger("flask_app")
    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)  # Default level
        handler = logging.StreamHandler()  # Console output
        log_format = "%(asctime)s | %(levelname)s | %(message)s"
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

custom_logger = setup_logging()
