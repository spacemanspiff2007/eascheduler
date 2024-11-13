import logging
from collections.abc import Generator, Iterable
from typing import Final, Literal, TypeAlias

from whenever import RepeatedTime, SkippedTime, SystemDateTime, Time

from eascheduler.helpers.time_replace import HINT_REPEATED, HINT_SKIPPED, RepeatedTimeBehavior, SkippedTimeBehavior


log = logging.getLogger('EAScheduler')


def _iter_nr(nrs: Iterable[int], lower: int, upper: int) -> Generator[int, None, None]:
    for nr in nrs:
        yield nr
    for nr in range(lower, upper):
        if nr not in nrs:
            yield nr


def _iter_date(*, reverse: bool = False) -> Generator[tuple[SystemDateTime, Time], None, None]:
    month_order = (3, 4, 11, 9, 10)
    hour_order = (2, 3, 0, 1)

    now = SystemDateTime.now()

    for month in _iter_nr(month_order if not reverse else reversed(month_order), 1, 13):
        for hour in _iter_nr(hour_order if not reverse else reversed(hour_order), 0, 24):
            start = SystemDateTime(now.year, month, 1)
            while start.month == month:
                yield start, Time(hour, 30)
                start = start.add(hours=24)


def find_time(*, reverse: bool) -> bool | tuple[Literal['forward', 'backward'], Time, Time]:

    # This has to be set here, even though it will always be overwritten in the except block
    dst_type: Literal['forward', 'backward'] = 'forward'

    for dt, time in _iter_date(reverse=reverse):
        try:
            dt.replace_time(time, disambiguate='raise')
        except (SkippedTime, RepeatedTime) as e:  # noqa: PERF203
            dst_type = 'forward' if isinstance(e, SkippedTime) else 'backward'
            break
    else:
        log.debug('No DST transition found')
        return False

    lower = time.replace(minute=0)
    upper = time.replace(minute=59, second=59, nanosecond=999_999_999)

    # check that both are invalid
    for t in (lower, upper):
        try:
            dt.replace_time(t, disambiguate='raise')
        except (SkippedTime, RepeatedTime):  # noqa: PERF203
            pass
        else:
            log.error(f'DST transition is valid when it should be invalid ({dt.date()} {t})!')
            return True

    # check that the next ones are valid
    for t in (upper.replace(hour=upper.hour - 1 if upper.hour >= 1 else 23),
              lower.replace(hour=lower.hour + 1 if lower.hour < 23 else 0)):  # noqa: PLR2004
        try:
            dt.replace_time(t, disambiguate='raise')
        except (SkippedTime, RepeatedTime):  # noqa: PERF203
            log.error(f'DST transition is invalid when it should be valid ({dt.date()} {t})!')
            return True

    return dst_type, lower, upper


class DstHandlingRequiredBase:
    def required(self, t: Time) -> bool:
        raise NotImplementedError()


class DstHandlingRequiredBool(DstHandlingRequiredBase):
    def __init__(self, value: bool) -> None:  # noqa: FBT001
        self.value: Final = value

    def required(self, t: Time) -> bool:  # noqa: ARG002
        return self.value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} value={self.value}>'


class DstHandlingRequiredDate(DstHandlingRequiredBase):
    def __init__(self, lower: Time, upper: Time) -> None:
        self.lower: Final = lower
        self.upper: Final = upper

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} lower={self.lower!s} upper={self.upper!s}>'

    def required(self, t: Time) -> bool:
        return self.lower <= t <= self.upper


TIME_FORWARD: DstHandlingRequiredBase | None = None
TIME_BACKWARD: DstHandlingRequiredBase | None = None


def _setup() -> None:
    global TIME_FORWARD, TIME_BACKWARD

    for r in (False, True):
        res = find_time(reverse=r)
        # error or not found
        if res is False or res is True:
            TIME_FORWARD = DstHandlingRequiredBool(res)
            TIME_BACKWARD = DstHandlingRequiredBool(res)
            break

        dst_type, lower, upper = res
        match dst_type:
            case 'forward':
                if TIME_FORWARD is not None:
                    msg = 'Forward DST transition already set'
                    raise ValueError(msg)
                TIME_FORWARD = DstHandlingRequiredDate(lower, upper)
            case 'backward':
                if TIME_BACKWARD is not None:
                    msg = 'Backward DST transition already set'
                    raise ValueError(msg)
                TIME_BACKWARD = DstHandlingRequiredDate(lower, upper)
            case _:
                msg = f'Invalid dst_type: {dst_type!r}'
                raise ValueError(msg)


HINT_CLOCK_FORWARD: TypeAlias = HINT_SKIPPED | None
HINT_CLOCK_BACKWARD: TypeAlias = HINT_REPEATED | None


def check_dst_handling(t: Time, forward: HINT_CLOCK_FORWARD,
                       backward: HINT_CLOCK_BACKWARD) -> tuple[HINT_SKIPPED, HINT_REPEATED]:

    # If the user supplies both we don't have to do anything
    if forward is not None and backward is not None:
        return forward, backward

    # Try to find DST time
    if TIME_FORWARD is None or TIME_BACKWARD is None:
        _setup()
        for to_del in ('_setup', 'find_time', '_iter_date', '_iter_nr'):
            del globals()[to_del]

        assert TIME_FORWARD is not None     # noqa: S101
        assert TIME_BACKWARD is not None    # noqa: S101

    if forward is None:
        if TIME_FORWARD.required(t):
            msg = 'Time is during a forward DST transition but no behavior set'
            raise ValueError(msg)
        forward = SkippedTimeBehavior.AFTER
    if backward is None:
        if TIME_BACKWARD.required(t):
            msg = 'Time is during a backward DST transition but no behavior set'
            raise ValueError(msg)
        backward = RepeatedTimeBehavior.EARLIER

    return forward, backward
