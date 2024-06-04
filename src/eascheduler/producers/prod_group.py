from __future__ import annotations

from typing import TYPE_CHECKING, Final, Iterable

from .base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from pendulum import DateTime


class GroupProducer(DateTimeProducerBase):
    __slots__ = ('_producers', )

    def __init__(self, producers: Iterable[DateTimeProducerBase]):
        super().__init__()
        self._producers: Final = tuple(producers)

    def get_next(self, dt: DateTime) -> DateTime:

        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503

            values = sorted(p.get_next(next_dt) for p in self._producers)
            next_dt = values[0]

            for value in values:
                if value > dt and ((f := self._filter) is None or not f.skip(value)):
                    return value