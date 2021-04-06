from eascheduler import SchedulerView
from eascheduler.executors import AsyncExecutor
from eascheduler.schedulers import AsyncScheduler

RUN = SchedulerView(AsyncScheduler(), AsyncExecutor)
