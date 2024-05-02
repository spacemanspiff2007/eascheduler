from eascheduler import SchedulerView
from eascheduler.old_executors import AsyncExecutor
from eascheduler.old_schedulers import AsyncScheduler

RUN = SchedulerView(AsyncScheduler(), AsyncExecutor)
