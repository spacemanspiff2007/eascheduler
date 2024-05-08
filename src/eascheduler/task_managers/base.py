from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from asyncio import Task


class TaskManagerBase:
    def create_task(self, coro, *, name: str | None = None) -> Task | None:
        raise NotImplementedError()
