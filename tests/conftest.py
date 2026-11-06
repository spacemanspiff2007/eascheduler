import os
from traceback import format_exc
from unittest.mock import patch

import pytest
from whenever import reset_system_tz

from eascheduler import default as default_scheduler_module
from eascheduler.errors import handler
from eascheduler.helpers import dst_param as dst_param_module
from eascheduler.producers import prod_sun as sun_module


@pytest.fixture
def system_tz_berlin(monkeypatch):
    try:
        with patch.dict(os.environ, {'TZ': 'Europe/Berlin'}):
            # update the time zone cache
            reset_system_tz()

            # reset the DST handler so it loads - when requested - with the new TZ
            monkeypatch.setattr(dst_param_module, 'TIME_FORWARD', None)
            monkeypatch.setattr(dst_param_module, 'TIME_BACKWARD', None)

            yield
    finally:
        reset_system_tz()  # don't forget to set the old time zone back!


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
