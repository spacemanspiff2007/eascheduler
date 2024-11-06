from traceback import format_exc

import pytest

from eascheduler import default as default_scheduler_module
from eascheduler.errors import handler
from eascheduler.producers import prod_sun as sun_module


@pytest.fixture(autouse=True)
def _reset_values(monkeypatch):
    sun_module.set_location(52.51870523376821, 13.376072914752532)

    monkeypatch.setattr(sun_module, 'SUN_CACHE', sun_module.SUN_CACHE.__class__())
    monkeypatch.setattr(default_scheduler_module, 'DEFAULT', None)

    yield

    # remove location
    assert hasattr(sun_module, 'OBSERVER')
    sun_module.OBSERVER = None

    if default := default_scheduler_module.DEFAULT:
        default._scheduler.remove_all()


@pytest.fixture(autouse=True)
def caught_exceptions(monkeypatch):
    exceptions = []
    traceback = []

    def proc_exception(e: Exception) -> None:
        exceptions.append(e)
        traceback.append(format_exc())

    monkeypatch.setattr(handler, '_EXCEPTION_HANDLER', proc_exception)

    yield exceptions

    # in case we clear the exceptions (if we expected one)
    if exceptions and traceback:
        for t in traceback:
            print()
            print(t)

    assert not exceptions
