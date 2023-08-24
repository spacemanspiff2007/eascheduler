from inspect import getargs
from unittest.mock import Mock

import pytest

from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.jobs import (
    CountdownJob, DawnJob, DayOfWeekJob, DuskJob, OneTimeJob, ReoccurringJob, SunriseJob, SunsetJob
)
from eascheduler.schedulers import AsyncScheduler


@pytest.mark.parametrize(
    'cls,name',
    [(cls, name) for cls in (ReoccurringJob, DayOfWeekJob, CountdownJob, OneTimeJob,
                             SunsetJob, SunriseJob, DuskJob, DawnJob)
     for name in dir(cls) if not name.startswith('_') and name not in ('get_next_run', 'remaining')]
)
def test_job_canceled(cls, name: str):

    obj = cls(None, lambda x: x)

    with pytest.raises(JobAlreadyCanceledException):
        func = getattr(obj, name)
        args, varargs, varkw = getargs(func.__code__)
        if varargs is None:
            varargs = []
        if varkw is None:
            varkw = []
        if len(args) + len(varargs) + len(varkw) > 1:
            func(None)
        else:
            func()


@pytest.mark.parametrize(
    'cls', (ReoccurringJob, DayOfWeekJob, CountdownJob, OneTimeJob, SunsetJob, SunriseJob, DuskJob, DawnJob))
async def test_callback(cls, async_scheduler: AsyncScheduler):

    job = cls(async_scheduler, None)
    job._next_run_callback = m = Mock()

    m.assert_not_called()
    job._set_next_run(300)
    m.assert_called_with(job)

    m.reset_mock()
    m.assert_not_called()
    job.cancel()
    m.assert_called_with(job)
