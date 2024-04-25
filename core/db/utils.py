import time
from functools import wraps
from typing import Type

from flask import current_app

from core.db import db


def transaction_retry_wrapper(max_retries: int, sleep_duration: float, error_type: Type[Exception]):
    """Execute a transaction with retries for a specified error type.

    This function wraps the provided 'function' in a database transaction and allows for retries
    in case of a specified error type. If an error of the specified type occurs during the
    transaction, the operation is retried up to a specified maximum number of times with a
    delay between retries.

    :param max_retries: The maximum number of retries in case of an error.
    :param sleep_duration: The duration to sleep between retry attempts.
    :param error_type: The type of error to catch and retry.
    :return: None
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for retry in range(1, max_retries + 1):
                try:
                    with db.session.begin():
                        func(*args, **kwargs)
                    break
                except error_type as transaction_error:
                    if retry < max_retries:
                        time.sleep(sleep_duration)
                        current_app.logger.warning(
                            "{func_name} failed with {transaction_error}. Retry count: {retry}.",
                            extra=dict(func_name=func.__name__, transaction_error=transaction_error, retry=retry),
                        )
                    else:
                        current_app.logger.error(
                            "Number of max retries exceeded for function '{func_name}'",
                            extra=dict(func_name=func.__name__),
                        )
                        raise transaction_error

        return wrapper

    return decorator
