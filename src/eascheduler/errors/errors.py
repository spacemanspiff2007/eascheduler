
class JobAlreadyCanceledException(Exception):
    pass


class OneTimeJobCanNotBeSkipped(Exception):
    pass


class UnknownWeekdayError(Exception):
    pass


class FirstRunInThePastError(Exception):
    pass
