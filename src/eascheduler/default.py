from eascheduler.builder import FilterBuilder, JobBuilder, TriggerBuilder
from eascheduler.executor import AsyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler


class DefaultJobBuilder(JobBuilder):
    triggers = TriggerBuilder
    filters = FilterBuilder


DEFAULT: DefaultJobBuilder | None = None


def get_default_scheduler() -> DefaultJobBuilder:
    global DEFAULT

    if DEFAULT is None:
        DEFAULT = DefaultJobBuilder(scheduler=AsyncScheduler(), executor=AsyncExecutor)
    return DEFAULT
