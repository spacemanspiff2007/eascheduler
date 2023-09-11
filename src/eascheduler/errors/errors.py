
class JobAlreadyCanceledException(Exception):
    pass


class UnknownWeekdayError(Exception):
    pass


class FirstRunInThePastError(Exception):
    pass


class BoundaryFunctionError(Exception):
    pass


class InfiniteLoopDetectedError(Exception):
    pass
