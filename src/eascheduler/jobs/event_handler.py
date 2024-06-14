from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from eascheduler.errors.handler import process_exception


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class JobEventHandler:
    __slots__ = ('_callbacks', )

    def __init__(self):
        self._callbacks: tuple[Callable[[JobBase], None], ...] = ()

    def register(self, callback: Callable[[JobBase], None]) -> bool:
        if callback in self._callbacks:
            return False
        self._callbacks += (callback, )
        return True

    def remove(self, callback: Callable[[JobBase], None]) -> bool:
        if callback in self._callbacks:
            return False
        self._callbacks = tuple(cb for cb in self._callbacks if cb is not callback)
        return True

    def clear(self):
        self._callbacks = ()

    def run(self, job: JobBase):
        for callback in self._callbacks:
            try:
                callback(job)
            except Exception as e:  # noqa: PERF203
                process_exception(e)
