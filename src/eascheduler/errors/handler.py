import logging
from typing import Any, Callable


def default_exception_handler(e: Exception) -> None:
    logging.getLogger('EAScheduler').error(e)


_EXCEPTION_HANDLER: Callable[[Exception], Any] = default_exception_handler


def set_exception_handler(handler: Callable[[Exception], Any]) -> None:
    global _EXCEPTION_HANDLER
    _EXCEPTION_HANDLER = handler


def process_exception(e: Exception) -> None:
    _EXCEPTION_HANDLER(e)
