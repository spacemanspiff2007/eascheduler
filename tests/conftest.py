import pendulum
import pytest

from eascheduler.jobs import job_sun


@pytest.fixture(autouse=True)
def reset_time():
    # reset time
    pendulum.set_test_now(None)

    # remove location
    assert hasattr(job_sun, 'OBSERVER')
    job_sun.OBSERVER = None
