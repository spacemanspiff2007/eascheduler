from asyncio import CancelledError
from traceback import format_exc

import pendulum
import pytest

from eascheduler.errors import handler
from eascheduler.triggers import prod_sun as sun_module


@pytest.fixture(autouse=True)
def _reset_values():
    sun_module.set_location(52.51870523376821, 13.376072914752532)

    yield

    # reset time
    pendulum.travel_back()

    # remove location
    assert hasattr(sun_module, 'OBSERVER')
    sun_module.OBSERVER = None


@pytest.fixture(autouse=True)
def caught_exceptions(monkeypatch):
    exceptions = []
    traceback = []

    def proc_exception(e: Exception):
        if not isinstance(e, CancelledError):
            exceptions.append(e)
            traceback.append(format_exc())

    monkeypatch.setattr(handler, 'HANDLER', proc_exception)

    yield exceptions

    # in case we clear the exceptions (if we expected one)
    if exceptions and traceback:
        for t in traceback:
            print('')
            print(t)
    assert not exceptions
