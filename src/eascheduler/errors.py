
class JobAlreadyCanceledException(Exception):
    pass


class OneTimeJobCanNotBeSkipped(Exception):
    pass


class UnknownWeekdayError(Exception):
    pass


class FirstRunNotInTheFutureError(Exception):
    pass
