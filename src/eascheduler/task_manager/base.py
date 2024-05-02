class TaskManagerBase:
    def create_task(self, coro, *, name: str | None = None):
        raise NotImplementedError()
