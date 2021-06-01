from inspect import getargs

import pytest

from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.jobs import (
    CountdownJob, DawnJob, DayOfWeekJob, DuskJob, OneTimeJob, ReoccurringJob, SunriseJob, SunsetJob
)


@pytest.mark.parametrize(
    'cls,name',
    [(cls, name) for cls in (ReoccurringJob, DayOfWeekJob, CountdownJob, OneTimeJob,
                             SunsetJob, SunriseJob, DuskJob, DawnJob)
     for name in dir(cls) if not name.startswith('_') and name not in ('get_next_run', )]
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
