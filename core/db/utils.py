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
        def wrapper(retries_left=max_retries, *args, **kwargs):
            error_dictionary = {}
            for retry in range(retries_left):
                try:
                    with db.session.begin():
                        func(*args, **kwargs)
                    break
                except error_type as transaction_error:
                    if retry < retries_left:
                        retries_left -= 1
                        time.sleep(sleep_duration)
                        error_dictionary["Failure With Retry"] = (
                            f"{func.__name__} failed with {str(transaction_error)}"
                            f"with {retries_left} retries remaining."
                        )
                    else:
                        error_dictionary["Max Retries Exceeded"] = (
                            f"Number of max retries exceeded " f"for function '{func.__name__}'"
                        )
                        current_app.logger.error(error_dictionary)
                        raise transaction_error
            if error_dictionary:
                current_app.logger.error(error_dictionary)

        return wrapper

    return decorator
