import logging
import os

_LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# DEFAULT_LOGGER_NAME = os.getenv("DEFAULT_LOGGER_NAME", "main")
LOGGER_FORMAT = os.getenv(
    "LOGGER_FORMAT",
    "[%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(funcName)s] %(message)s",
)
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", "INFO")


def setup_logging(
    level: int | str | None = LOGGER_LEVEL,
    format: str = LOGGER_FORMAT,
) -> logging.Logger:
    # Get the root logger
    logger = logging.getLogger()

    # Remove all existing handlers (useful if a library called basicConfig, e.g.)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    logger.addHandler(console_handler)

    # Set log level
    if isinstance(level, str):
        # Logging level specified as a string, e.g., "DEBUG"
        level = _LOG_LEVEL_MAP.get(level.upper(), LOGGER_LEVEL)
    elif level is None:
        # No logging level specified, use the default
        level = LOGGER_LEVEL
    logger.setLevel(level)

    return logger
