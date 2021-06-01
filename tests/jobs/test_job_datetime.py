import asyncio
from asyncio import create_task
from datetime import datetime, time, timedelta
from typing import List

import pytest
from pendulum import from_timestamp

from eascheduler.const import local_tz
from eascheduler.errors import FirstRunInThePastError
from eascheduler.executors import AsyncExecutor
from eascheduler.jobs.job_base_datetime import DateTimeJobBase
from eascheduler.schedulers import AsyncScheduler, scheduler_async
from tests.helper import cmp_local, set_now, utc_ts


@pytest.mark.asyncio
async def test_boundary():
    async def bla():
        pass

    set_now(2001, 1, 1, 1)

    s = AsyncScheduler()
    j = DateTimeJobBase(s, AsyncExecutor(bla))
    s.add_job(j)

    j._next_run_base = utc_ts(2001, 1, 1, 12)
    j._apply_boundaries()
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
async def test_func_boundary_changes_self():
    async def bla():
        pass

    s = AsyncScheduler()
    j = DateTimeJobBase(s, AsyncExecutor(bla))
    s.add_job(j)

    set_now(2001, 1, 1, 7, 10)
    j._schedule_first_run(None)
    assert from_timestamp(j._next_run_base).in_tz(local_tz).naive() == datetime(2001, 1, 1, 7, 10, 0)

    # Boundary function test
    def test_func(obj):
        assert isinstance(obj, datetime)
        j.offset(timedelta(hours=1))
        j.earliest(time(8))
        j.latest(time(9))
        return obj

    j.boundary_func(test_func)
    assert from_timestamp(j._next_run).in_tz(local_tz).naive() == datetime(2001, 1, 1, 8, 10, 0)

    j.cancel()


@pytest.mark.asyncio
async def test_func_boundary():
    async def bla():
        pass

    s = AsyncScheduler()
    j = DateTimeJobBase(s, AsyncExecutor(bla))
    s.add_job(j)

    set_now(2001, 1, 1, 7, 10)
    j._schedule_first_run(1)

    # Boundary function test
    def test_func(obj):
        assert obj == datetime(2001, 1, 1, 7, 10, 1)
        return obj

    j.boundary_func(test_func)
    assert j.get_next_run() == datetime(2001, 1, 1, 7, 10, 1)

    j.cancel()


@pytest.mark.asyncio
async def test_initialize():
    s = AsyncScheduler()
    j = DateTimeJobBase(s, lambda x: x)

    set_now(2001, 1, 1, 12, 0, 0)

    # Now
    j._schedule_first_run(None)
    cmp_local(j._next_run_base, datetime(2001, 1, 1, 12, 0, 0))

    # Diff from now
    j._schedule_first_run(timedelta(days=1, minutes=30))
    cmp_local(j._next_run_base, datetime(2001, 1, 2, 12, 30))

    j._schedule_first_run(120)
    cmp_local(j._next_run_base, datetime(2001, 1, 1, 12, 2))

    j._schedule_first_run(181.5)
    cmp_local(j._next_run_base, datetime(2001, 1, 1, 12, 3, 1, 500_000))

    # Specified time
    j._schedule_first_run(time(1, 20, 30))
    cmp_local(j._next_run_base, datetime(2001, 1, 2, 1, 20, 30))

    # Specified time
    j._schedule_first_run(datetime(2001, 1, 1, 12, 20, 30))
    cmp_local(j._next_run_base, datetime(2001, 1, 1, 12, 20, 30))

    with pytest.raises(FirstRunInThePastError) as e:
        j._schedule_first_run(datetime(2001, 1, 1, 1, 20, 30))
    assert str(e.value) in (
        'First run can not be in the past! Now: 2001-01-01T12:00:00+01:00, run: 2001-01-01T01:20:30+01:00',
        'First run can not be in the past! Now: 2001-01-01T12:00:00+00:00, run: 2001-01-01T01:20:30+00:00',
    )


@pytest.mark.asyncio
async def test_worker_cancel(monkeypatch):
    all_tasks: List[asyncio.Future] = []

    def create_collect_task(coro):
        t = create_task(coro)
        all_tasks.append(t)
        return t

    monkeypatch.setattr(scheduler_async, 'create_task', create_collect_task)

    s = AsyncScheduler()
    j = DateTimeJobBase(s, lambda: 1 / 0)

    set_now(2001, 1, 1, 12, 0, 0)

    j._schedule_first_run(datetime(2020, 1, 1, 12, 30))
    for i in range(10):
        await asyncio.sleep(0.001)
        j.offset(timedelta(minutes=i))
    j.cancel()

    assert s.worker is None

    await asyncio.sleep(0.02)

    for task in all_tasks:
        assert task.cancelled(), task
