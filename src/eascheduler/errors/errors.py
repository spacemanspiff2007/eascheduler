class EaSchedulerError(Exception):
    pass


class JobNotLinkedToSchedulerError(EaSchedulerError):
    pass


class JobAlreadyCanceledException(EaSchedulerError):
    pass


class JobExecutionTimeIsNotSetError(EaSchedulerError):
    pass


class UnknownWeekdayError(EaSchedulerError):
    pass


class ScheduledRunInThePastError(EaSchedulerError):
    pass


class BoundaryFunctionError(EaSchedulerError):
    pass


class InfiniteLoopDetectedError(EaSchedulerError):
    pass


class JobAlreadyFinishedError(EaSchedulerError):
    pass
