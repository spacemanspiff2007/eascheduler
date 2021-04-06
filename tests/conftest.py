import pytest
import pendulum


@pytest.fixture(autouse=True)
def reset_time():
    pendulum.set_test_now(None)
