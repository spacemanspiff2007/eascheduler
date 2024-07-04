from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from asyncio import Task
    from collections.abc import Coroutine


class TaskManagerBase:
    __slots__ = ()

    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        raise NotImplementedError()
