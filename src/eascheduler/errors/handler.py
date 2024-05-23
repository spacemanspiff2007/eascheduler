import logging
from typing import Any, Callable


HANDLER: Callable[[Exception], Any] = lambda x: logging.getLogger('EAScheduler').error(x)


def set_exception_handler(handler: Callable[[Exception], Any]):
    global HANDLER
    HANDLER = handler


def process_exception(e: Exception):
    HANDLER(e)
