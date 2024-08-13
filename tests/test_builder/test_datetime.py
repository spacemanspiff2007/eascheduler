import asyncio
from datetime import datetime

import pytest
from whenever import SystemDateTime, patch_current_time

from eascheduler.builder import FilterBuilder, JobBuilder, TriggerBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import AlwaysError, assert_called_at


async def test_call():
    calls = []

    def append():
        calls.append(SystemDateTime.now())

    now = SystemDateTime.now()
    dst = now.add(seconds=1).replace(nanosecond=0, disambiguate='raise')

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    builder.at(
        TriggerBuilder.time(dst.time()),
        append
    )

    await asyncio.sleep((dst - now).in_seconds() + 0.01)

    assert_called_at(calls, dst)


@pytest.fixture()
async def builder():
    with patch_current_time(SystemDateTime(2001, 1, 1, 12), keep_ticking=False):
        s = AsyncScheduler()
        yield JobBuilder(s, SyncExecutor)
        s.remove_all()


async def test_build(builder):
    job = builder.at(TriggerBuilder.time('14:00:00'), AlwaysError())
    assert job.next_run_datetime == datetime(2001, 1, 1, 14, 0, 0)


async def test_build_action(builder):
    job = builder.at(TriggerBuilder.time('14:00:00').offset('PT1H'), AlwaysError())
    assert job.next_run_datetime == datetime(2001, 1, 1, 15, 0, 0)


async def test_build_filter(builder):
    job = builder.at(TriggerBuilder.time('14:00:00').only_on(FilterBuilder.days('2')), AlwaysError())
    assert job.next_run_datetime == datetime(2001, 1, 2, 14, 0, 0)


async def test_build_action_filter(builder):
    job = builder.at(
        TriggerBuilder.time('14:00:00').offset('PT1H').only_on(FilterBuilder.days('2')),
        AlwaysError()
    )
    assert job.next_run_datetime == datetime(2001, 1, 2, 15, 0, 0)


async def test_build_action_filter_all(builder):
    job = builder.at(
        TriggerBuilder.time('14:00:00').offset('PT1H').only_on(
            FilterBuilder.all(FilterBuilder.days('2-7'), FilterBuilder.weekdays('Wed'))
        ),
        AlwaysError()
    )
    assert job.next_run_datetime == datetime(2001, 1, 3, 15, 0, 0)


async def test_build_action_filter_any(builder):
    job = builder.at(
        TriggerBuilder.time('14:00:00').offset('PT1H').only_on(
            FilterBuilder.any(FilterBuilder.days('2-7'), FilterBuilder.weekdays('Wed'))
        ),
        AlwaysError()
    )
    assert job.next_run_datetime == datetime(2001, 1, 2, 15, 0, 0)


async def test_build_many(builder):
    job = builder.at(
        TriggerBuilder.group(
            TriggerBuilder.time('14:00:00'), TriggerBuilder.time('15:00:00')
        ),
        AlwaysError()
    )
    assert job.next_run_datetime == datetime(2001, 1, 1, 14)
