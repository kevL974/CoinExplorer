"""Connection utilities: settings parsing and retry decorators for HBase and Kafka."""
import logging
from typing import Callable, Tuple

from thriftpy2.transport.base import TTransportException

logger = logging.getLogger(__name__)


def is_valid_connection_setting_format(connection_settings: str) -> bool:
    """Check that a connection string contains the expected '<host>:<port>' separator.

    :param connection_settings: connection string to validate.
    :return: True if the string is non-empty and contains ':', False otherwise.
    """
    if connection_settings:
        return ":" in connection_settings
    return False


def parse_connection_settings(connection_settings: str) -> Tuple[str, int]:
    """Parse a '<host>:<port>' connection string into a (host, port) tuple.

    :param connection_settings: a string like '<host>:<port>'.
    :return: tuple (host, port) where port is an integer.
    :raises ValueError: if the string does not match the expected format.
    """
    if not is_valid_connection_setting_format(connection_settings):
        raise ValueError(f"Bad connection settings {connection_settings}")

    settings = connection_settings.split(":")
    host = settings[0]
    port = int(settings[1])
    return host, port


def retry_connection_on_brokenpipe(max_retries: int = 5):
    """Decorator factory that retries a function on BrokenPipeError.

    Wraps a function so that if it raises BrokenPipeError, it is retried up to
    `max_retries` times before raising a generic Exception.

    :param max_retries: maximum number of retry attempts (must be > 0).
    :return: decorator that applies the retry logic to the wrapped function.
    :raises ValueError: if max_retries is not strictly positive.
    """
    if max_retries <= 0:
        raise ValueError(f"max_retries must be > 0 instead of {max_retries}")

    def retry_connection(function: Callable):
        def retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return function(*args, **kwargs)
                except BrokenPipeError:
                    logger.warning("Try n°%d failed, retry...", retries + 1)
                    retries += 1
            raise Exception("Maximum retries exceeded")

        return retry

    return retry_connection


def retry_connection_on_ttransportexception(max_retries: int = 5):
    """Decorator factory that retries a function on TTransportException (HBase/Thrift).

    Wraps a function so that if it raises TTransportException, it is retried up to
    `max_retries` times before raising a generic Exception.

    :param max_retries: maximum number of retry attempts (must be > 0).
    :return: decorator that applies the retry logic to the wrapped function.
    :raises ValueError: if max_retries is not strictly positive.
    """
    if max_retries <= 0:
        raise ValueError(f"max_retries must be > 0 instead of {max_retries}")

    def retry_connection(function: Callable):
        def retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return function(*args, **kwargs)
                except TTransportException:
                    logger.warning("Try n°%d failed, retry...", retries + 1)
                    retries += 1
            raise Exception("Maximum retries exceeded")

        return retry

    return retry_connection
