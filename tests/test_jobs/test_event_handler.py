from eascheduler.jobs.event_handler import JobEventHandler


# noinspection PyTypeChecker
def test_handler():

    h = JobEventHandler()

    calls_1 = []
    calls_2 = []

    def cb_1(job):
        calls_1.append(job)

    def cb_2(job):
        calls_2.append(job)

    # run without callbacks
    h.run(None)
    assert not calls_1

    # Register both
    for _ in range(10):
        h.register(cb_1)
        h.register(cb_2)

    h.run(None)
    assert calls_1 == [None]
    assert calls_2 == [None]

    # Remove one callback
    calls_1.clear()
    calls_2.clear()
    for _ in range(10):
        h.remove(cb_1)

    h.run(None)
    assert calls_1 == []
    assert calls_2 == [None]

    # Clear all
    h.clear()
    calls_1.clear()
    calls_2.clear()

    h.run(None)
    assert calls_1 == []
    assert calls_2 == []