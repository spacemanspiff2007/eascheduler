from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Literal

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from pendulum import DateTime


class DateTimeProducerBase:
    def get_next(self, now: DateTime, dt: DateTime) -> DateTime:
        raise NotImplementedError()


class BaseDateTimeOperation:
    NAME: str

    def apply(self, dt: DateTime) -> DateTime | None:
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


def not_infinite_loop() -> Generator[Literal[True], None, None]:
    for _ in range(100_000):
        yield True

    raise InfiniteLoopDetectedError()