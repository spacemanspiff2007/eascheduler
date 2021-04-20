import pendulum
import pytest

from eascheduler.errors import handler
from eascheduler.jobs import job_sun


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

    def proc_exception(e: Exception):
        exceptions.append(e)

    monkeypatch.setattr(handler, 'HANDLER', proc_exception)

    yield exceptions

    assert not exceptions
