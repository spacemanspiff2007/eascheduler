import inspect
from asyncio import CancelledError
from traceback import format_exc

import pendulum
import pytest
from pendulum import DateTime, UTC

from eascheduler import jobs as job_module
from eascheduler.errors import handler
from eascheduler.jobs import job_sun
from eascheduler.schedulers import AsyncScheduler


@pytest.fixture(autouse=True)
def reset_values():
    # reset time
    pendulum.set_test_now(None)

    # remove location
    assert hasattr(job_sun, 'OBSERVER')
    job_sun.OBSERVER = None


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


@pytest.fixture
def async_scheduler():
    s = AsyncScheduler()

    yield s

    s.cancel_all()


@pytest.fixture(autouse=True)
def patch_advance_time(monkeypatch):
    found = 0
    for name, cls in inspect.getmembers(job_module, lambda x: hasattr(x, '_advance_time')):
        found += 1
        func_obj = getattr(cls, '_advance_time')

        def wrap_advance(self, utc_dt: DateTime, func=func_obj) -> DateTime:
            assert utc_dt.tz is UTC
            return func(self, utc_dt)

        monkeypatch.setattr(cls, '_advance_time', wrap_advance)

    assert found > 5
