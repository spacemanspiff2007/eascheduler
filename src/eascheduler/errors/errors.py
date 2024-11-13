class EaSchedulerError(Exception):
    pass


class JobNotLinkedToSchedulerError(EaSchedulerError):
    pass


class JobAlreadyCanceledError(EaSchedulerError):
    pass


class JobExecutionTimeIsNotSetError(EaSchedulerError):
    pass


class JobAlreadyFinishedError(EaSchedulerError):
    pass


class UnknownWeekdayError(EaSchedulerError):
    pass


class ScheduledRunInThePastError(EaSchedulerError):
    pass


class BoundaryFunctionError(EaSchedulerError):
    pass


class InfiniteLoopDetectedError(EaSchedulerError):
    pass


class LocationNotSetError(EaSchedulerError):
    pass


class HolidaysNotSetUpError(EaSchedulerError):
    pass
