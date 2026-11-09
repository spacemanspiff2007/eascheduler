import logging
from typing import Final, TypeAlias

from whenever import SYSTEM_TZ, Time, ZonedDateTime

from eascheduler.helpers.time_replace import HINT_REPEATED, HINT_SKIPPED, RepeatedTimeBehavior, SkippedTimeBehavior


log = logging.getLogger('EAScheduler')


HINT_CLOCK_FORWARD: TypeAlias = HINT_SKIPPED | None
HINT_CLOCK_BACKWARD: TypeAlias = HINT_REPEATED | None


def check_dst_handling(t: Time, forward: HINT_CLOCK_FORWARD,
                       backward: HINT_CLOCK_BACKWARD) -> tuple[HINT_SKIPPED, HINT_REPEATED]:

    # If the user supplies both we don't have to do anything
    if forward is not None and backward is not None:
        return forward, backward

    times_forward, times_backward = _get_transition_times()

    if forward is None:
        for t_l, t_h in times_forward:
            if t_l <= t <= t_h:
                msg = 'Time is during a forward DST transition but no behavior set'
                raise ValueError(msg)
        forward = SkippedTimeBehavior.AFTER
    if backward is None:
        for t_l, t_h in times_backward:
            if t_l <= t <= t_h:
                msg = 'Time is during a backward DST transition but no behavior set'
                raise ValueError(msg)
        backward = RepeatedTimeBehavior.EARLIER

    return forward, backward


def _window_from_transition(transition: ZonedDateTime) -> tuple[bool, Time, Time]:
    before_transition: Final = transition.subtract(nanoseconds=1)

    # it's a forward transition
    if not before_transition.is_repeated():
        return (
            True,
            before_transition.to_plain().add(nanoseconds=1, naive_arithmetic_ok=True).time(),
            transition.to_plain().subtract(nanoseconds=1, naive_arithmetic_ok=True).time()
        )

    # it's a backward transition
    return False, transition.to_plain().time(), before_transition.to_plain().time()


def _get_transition_times() -> tuple[list[tuple[Time, Time]], list[tuple[Time, Time]]]:
    now = ZonedDateTime.now(SYSTEM_TZ)
    year: Final = now.year + 1

    forward: Final[list[tuple[Time, Time]]] = []
    backward: Final[list[tuple[Time, Time]]] = []

    obj: ZonedDateTime | None = ZonedDateTime(year, 1, 1, tz=SYSTEM_TZ)

    while (obj := obj.next_transition()) is not None and obj.year == year:
        is_forward, start, stop = _window_from_transition(obj)
        if is_forward:
            forward.append((start, stop))
        else:
            backward.append((start, stop))

    return forward, backward
