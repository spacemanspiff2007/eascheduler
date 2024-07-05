from asyncio import Task, create_task
from collections import OrderedDict, deque
from collections.abc import Coroutine, Hashable
from enum import Enum
from typing import Final

from typing_extensions import override

from eascheduler.task_managers.base import TaskManagerBase


class SequentialTaskPolicy(str, Enum):
    SKIP = 'skip'
    SKIP_FIRST = 'skip_first'
    SKIP_LAST = 'skip_last'


POLICY_SKIP = SequentialTaskPolicy.SKIP
POLICY_SKIP_FIRST = SequentialTaskPolicy.SKIP_FIRST
POLICY_SKIP_LAST = SequentialTaskPolicy.SKIP_LAST


class SequentialTaskManagerBase(TaskManagerBase):
    __slots__ = ('task', )

    def __init__(self) -> None:
        self.task: Task | None = None

    def _get_next_task(self) -> None | tuple[Coroutine, str | None]:
        raise NotImplementedError()

    def _task_start(self) -> Task | None:
        if self.task is not None:
            return None
        return self._task_done(None)

    def _task_done(self, done_task: Task | None) -> Task | None:
        if done_task is self.task:
            self.task = None

        if (next_obj := self._get_next_task()) is None:
            return None

        coro, name = next_obj
        self.task = task = create_task(coro, name=name)
        task.add_done_callback(self._task_done)
        return task


class SequentialTaskManager(SequentialTaskManagerBase):
    __slots__ = ('queue', )

    def __init__(self) -> None:
        super().__init__()
        self.queue: Final[deque[tuple[Coroutine, str | None]]] = deque()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__:s} running={self.task is not None} queue={len(self.queue):d}>'

    @override
    def _get_next_task(self) -> None | tuple[Coroutine, str | None]:
        if not (queue := self.queue):
            return None
        return queue.popleft()

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        self.queue.append((coro, name))
        return self._task_start()


class LimitingSequentialTaskManager(SequentialTaskManager):
    __slots__ = ('max_queue', 'action')

    def __init__(self, max_queue: int, action: SequentialTaskPolicy | str = POLICY_SKIP) -> None:
        super().__init__()
        if not isinstance(max_queue, int) or max_queue < 1:
            raise ValueError()

        self.max_queue: Final = max_queue
        self.action: Final[SequentialTaskPolicy] = \
            SequentialTaskPolicy(action) if not isinstance(action, SequentialTaskPolicy) else action

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__:s} running={self.task is not None} coros={len(self.queue):d} '
            f'max_queue={self.max_queue:d} action={self.action.value}>'
        )

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:

        if len(queue := self.queue) >= self.max_queue:
            if (action := self.action) is POLICY_SKIP:
                coro.close()
                return None

            if action is POLICY_SKIP_FIRST:
                queue.popleft()[0].close()
            elif action is POLICY_SKIP_LAST:
                queue.pop()[0].close()
            else:
                raise ValueError()

        queue.append((coro, name))
        return self._task_start()


class SequentialDeduplicatingTaskManager(SequentialTaskManagerBase):
    __slots__ = ('queue', )

    def __init__(self) -> None:
        super().__init__()
        self.queue: Final[OrderedDict[Hashable, tuple[Coroutine, str | None]]] = OrderedDict()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__:s} running={self.task is not None} queue={len(self.queue):d}>'

    @override
    def _get_next_task(self) -> None | tuple[Coroutine, str | None]:
        if not (queue := self.queue):
            return None
        return queue.popitem(last=False)[1]

    # noinspection PyMethodOverriding
    @override
    def create_task(self, coro: Coroutine, key: Hashable, *, name: str | None = None) -> Task | None:   # type: ignore[override]
        queue = self.queue
        if (rem_coro := queue.pop(key, None)) is not None:
            rem_coro[0].close()

        queue[key] = (coro, name)
        return self._task_start()
