from datetime import time, datetime
from functools import partial

import pytest

from eascheduler import SchedulerView
from eascheduler import set_location
from eascheduler.executors import SyncExecutor
from eascheduler.schedulers import AsyncScheduler
from tests.helper import set_now


@pytest.fixture
def view():
    obj = AsyncScheduler()
    v = SchedulerView(obj, SyncExecutor)
    yield v
    obj.cancel_all()


@pytest.mark.asyncio
async def test_at(view: SchedulerView):
    s = view._scheduler

    now = partial(set_now, 2001, 1, 1)
    now(12)

    view.at(time(11), lambda x: x)
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 2, 11)

    view.at(time(13), lambda x: x)
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 1, 13)

    view.at(5, lambda x: x)
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 1, 12, 0, 5)


@pytest.mark.asyncio
async def test_every(view: SchedulerView):
    s = view._scheduler

    now = partial(set_now, 2001, 1, 1)
    now(12)

    view.every(5, 15, lambda x: x)
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 1, 12, 0, 5)

    now(12, 0, 6)
    s.jobs[0]._update_base_time()
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 1, 12, 0, 20)

    now(12, 0, 21)
    s.jobs[0]._update_base_time()
    assert s.jobs[0].get_next_run() == datetime(2001, 1, 1, 12, 0, 35)


@pytest.mark.asyncio
async def test_job_insert_at(view: SchedulerView):
    j = view.at(None, lambda x: 1 / 0)
    assert j is view._scheduler.jobs[0]
    assert j in view._scheduler.job_objs


@pytest.mark.asyncio
async def test_job_insert_countdown(view: SchedulerView):
    j = view.countdown(5, lambda x: 1 / 0)
    assert j is view._scheduler.jobs[0]
    assert j in view._scheduler.job_objs


@pytest.mark.asyncio
async def test_job_insert_every(view: SchedulerView):
    j = view.every(None, 5, lambda x: 1 / 0)
    assert j is view._scheduler.jobs[0]
    assert j in view._scheduler.job_objs


@pytest.mark.asyncio
async def test_job_insert_on_day_of_week(view: SchedulerView):
    j = view.on_day_of_week(time(5), 'Mon', lambda x: 1 / 0)
    assert j is view._scheduler.jobs[0]
    assert j in view._scheduler.job_objs

    # Test helper functions, too!
    view.on_weekends(time(5), lambda x: 1 / 0)
    view.on_workdays(time(5), lambda x: 1 / 0)


@pytest.mark.parametrize('name', ('on_sun_dawn', 'on_sunrise', 'on_sunset', 'on_sun_dusk'))
@pytest.mark.asyncio
async def test_job_insert_on_sunrise(view: SchedulerView, name: str):
    set_location(52.5185537, 13.3758636, 43)
    j = getattr(view, name)(lambda x: 1 / 0)
    assert j is view._scheduler.jobs[0]
    assert j in view._scheduler.job_objs
