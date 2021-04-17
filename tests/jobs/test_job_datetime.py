from datetime import time, datetime, timedelta
import pytest
from eascheduler.jobs.job_datetime_base import DateTimeJobBase
from tests.helper import utc_ts
from eascheduler.schedulers import AsyncScheduler
from eascheduler.executors import AsyncExecutor
from eascheduler.const import local_tz
from eascheduler.errors import FirstRunNotInTheFutureError
from tests.helper import set_now
from pendulum import from_timestamp


@pytest.mark.asyncio
async def test_boundary():
    async def bla():
        pass

    s = AsyncScheduler()
    j = DateTimeJobBase(s, AsyncExecutor(bla))
    s.add_job(j)

    j._next_base = utc_ts(2001, 1, 1, 12)
    j._update_run_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    # Latest modifier
    j.latest(time(8, 30))
    assert j.get_next_run() == datetime(2001, 1, 1, 8, 30)
    j.latest(None)
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    # Earliest
    j.earliest(time(14, 45))
    assert j.get_next_run() == datetime(2001, 1, 1, 14, 45)
    j.earliest(None)
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    # Offset test
    j.offset(timedelta(hours=1, minutes=15))
    assert j.get_next_run() == datetime(2001, 1, 1, 13, 15)
    j.offset(timedelta(hours=1, minutes=-15))
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 45)
    j.offset(timedelta(hours=-1, minutes=-15))
    assert j.get_next_run() == datetime(2001, 1, 1, 10, 45)
    j.offset(None)
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    # Jitter test
    for i in range(1000):
        j.jitter(-30)
        assert datetime(2001, 1, 1, 11, 59, 30) <= j.get_next_run() <= datetime(2001, 1, 1, 12, 0, 30)
        j.jitter(15)
        assert datetime(2001, 1, 1, 11, 59, 45) <= j.get_next_run() <= datetime(2001, 1, 1, 12, 0, 15)
        j.jitter(-5, 25)
        assert datetime(2001, 1, 1, 11, 59, 55) <= j.get_next_run() <= datetime(2001, 1, 1, 12, 0, 25)
    j.jitter(None)
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    # Boundary function test
    def test_func(obj):
        assert isinstance(obj, datetime)
        return obj.replace(hour=obj.hour + 1)

    j.boundary_func(test_func)
    assert j.get_next_run() == datetime(2001, 1, 1, 13, 0)
    j.boundary_func(None)
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0)

    s.cancel_all()


@pytest.mark.asyncio
async def test_func_boundary():
    async def bla():
        pass

    s = AsyncScheduler()
    j = DateTimeJobBase(s, AsyncExecutor(bla))
    s.add_job(j)

    set_now(2001, 1, 1, 7, 10)
    j._initialize_base_time(None)

    # Boundary function test
    def test_func(obj):
        assert isinstance(obj, datetime)
        j.offset(timedelta(hours=1))
        j.earliest(time(8))
        j.latest(time(9))
        return obj

    j.boundary_func(test_func)
    assert j.get_next_run() == datetime(2001, 1, 1, 8, 10)

    j.cancel()


@pytest.mark.asyncio
async def test_initialize():
    s = AsyncScheduler()
    j = DateTimeJobBase(s, lambda x: x)

    set_now(2001, 1, 1, 12, 0, 0)

    # Now
    j._initialize_base_time(None)
    assert from_timestamp(j._next_base).in_tz(local_tz).naive() == datetime(2001, 1, 1, 12, 0, 0, 1)

    # Diff from now
    j._initialize_base_time(timedelta(days=1, minutes=30))
    assert from_timestamp(j._next_base).in_tz(local_tz).naive() == datetime(2001, 1, 2, 12, 30)

    j._initialize_base_time(120)
    assert from_timestamp(j._next_base).in_tz(local_tz).naive() == datetime(2001, 1, 1, 12, 2)

    j._initialize_base_time(181.5)
    assert from_timestamp(j._next_base).in_tz(local_tz).naive() == datetime(2001, 1, 1, 12, 3, 1, 500_000)

    # Specified time
    j._initialize_base_time(time(1, 20, 30))
    assert from_timestamp(j._next_base).in_tz(local_tz).naive() == datetime(2001, 1, 2, 1, 20, 30)

    with pytest.raises(FirstRunNotInTheFutureError) as e:
        j._initialize_base_time(datetime(2001, 1, 1, 1, 20, 30))
    assert str(e.value) in (
        'First run must be in the future! Now: 2001-01-01T12:00:00+01:00, run: 2001-01-01T02:20:30+01:00',
        'First run must be in the future! Now: 2001-01-01T12:00:00+00:00, run: 2001-01-01T01:20:30+00:00',
    )
