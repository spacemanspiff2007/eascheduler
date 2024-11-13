from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from collections.abc import Iterable

    from whenever import Instant


class GroupProducer(DateTimeProducerBase):
    __slots__ = ('_producers', )

    def __init__(self, producers: Iterable[DateTimeProducerBase]) -> None:
        super().__init__()
        self._producers: Final = tuple(producers)

    def get_next(self, dt: Instant) -> Instant:   # type: ignore[return]

        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503

            values = sorted(p.get_next(next_dt) for p in self._producers)
            next_dt = values[0]

            for value in values:
                if value > dt and ((f := self._filter) is None or f.allow(value.to_system_tz())):
                    return value
