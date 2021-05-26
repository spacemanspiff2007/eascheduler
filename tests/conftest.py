import pendulum
import pytest
from asyncio import CancelledError
from traceback import format_exc

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

    if traceback:
        for t in traceback:
            print('')
            print(t)
    assert not exceptions


@pytest.fixture
def async_scheduler():
    s = AsyncScheduler()

    yield s

    s.cancel_all()
