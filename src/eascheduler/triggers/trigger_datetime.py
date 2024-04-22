from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .base import not_infinite_loop
from .trigger_operations import sort_trigger_operations


if TYPE_CHECKING:
    from pendulum import DateTime

    from .base import BaseDateTimeOperation, DateTimeProducerBase


class DateTimeTrigger:
    def __init__(self, producer: DateTimeProducerBase):
        super().__init__()
        self.producer: Final = producer
        self.operations: tuple[BaseDateTimeOperation, ...] = ()

    def get_next(self, now: DateTime, dt: DateTime) -> DateTime:

        while not_infinite_loop():  # noqa: RET503

            # the producer should always return in local timezone!
            next_dt = self.producer.get_next(now, dt)

            for b in self.operations:
                if (next_dt := b.apply(next_dt)) is None:
                    break
            else:
                # if we are in the future we have the next run
                if next_dt > now:
                    return next_dt

            dt = next_dt

    def add(self, op: BaseDateTimeOperation) -> bool:
        operations = {o.NAME: o for o in self.operations}

        if (existing := operations.get(op.NAME)) is not None and existing == op:
            return False

        operations[op.NAME] = op
        self.operations = tuple(sorted(operations.values(), key=sort_trigger_operations))
        return True

    def remove(self, name: str) -> bool:
        operations = {o.NAME: o for o in self.operations}

        if operations.pop(name, None) is None:
            return False

        self.operations = tuple(operations.values())
        return True
