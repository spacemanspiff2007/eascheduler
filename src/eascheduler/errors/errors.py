class EaSchedulerError(Exception):
    pass


class JobAlreadyCanceledException(EaSchedulerError):
    pass


class UnknownWeekdayError(EaSchedulerError):
    pass


class FirstRunInThePastError(EaSchedulerError):
    pass


class BoundaryFunctionError(EaSchedulerError):
    pass


class InfiniteLoopDetectedError(EaSchedulerError):
    pass
