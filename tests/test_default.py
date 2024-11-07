import asyncio
import os
import re
from datetime import timedelta
from pathlib import Path
from textwrap import dedent

import pytest

from eascheduler import get_default_scheduler
from tests.helper import CountDownHelper


async def test_countdown() -> None:

    calls = CountDownHelper()
    async def await_call() -> None:
        calls()

    builder = get_default_scheduler()
    job = calls.link_job(builder.countdown(0.1, await_call))

    calls.reset()
    assert job.status.is_running

    for _ in range(10):
        await asyncio.sleep(0.02)
        calls.reset()

    calls.assert_not_called()
    await asyncio.sleep(0.15)

    calls.assert_called()
    assert job.status.is_paused


async def test_examples() -> None:
    # readme example start
    import eascheduler

    async def my_coro() -> None:
        print('Hello')

    # If you want something easy that you can use out of the box just use the default scheduler
    scheduler = eascheduler.get_default_scheduler()

    # -------------------------------------------------------------------------------------------------------
    # Different job types
    # -------------------------------------------------------------------------------------------------------

    # Run once in 30s
    job_once = scheduler.once(30, my_coro)

    # Countdown
    countdown = scheduler.countdown(30, my_coro)
    countdown.reset()               # make countdown start (again)
    countdown.stop()                # stop countdown
    countdown.set_countdown(15)     # set different countdown time which will be used for the next reset call

    # Trigger job which runs continuously, e.g.

    # every day at 8
    job_every = scheduler.at(scheduler.triggers.time('08:00:00'), my_coro)
    # for the first time in 10 mins, then every hour
    job_every = scheduler.at(scheduler.triggers.interval(600, 3600), my_coro)

    # -------------------------------------------------------------------------------------------------------
    # Restricting the trigger with a filter.
    # Only when the filter condition passes the time will be taken as the next time

    # every Fr-So at 8
    scheduler.at(
        scheduler.triggers.time('08:00:00').only_at(scheduler.filters.weekdays('Fr-So')),
        my_coro
    )

    # Triggers can be grouped
    # Mo-Fr at 7, Sa at 8
    scheduler.at(
        scheduler.triggers.group(
            scheduler.triggers.time('07:00:00').only_at(scheduler.filters.weekdays('Mo-Fr')),
            scheduler.triggers.time('08:00:00').only_at(scheduler.filters.weekdays('Fr-So')),
        ),
        my_coro
    )

    # Filters can be grouped with any or all
    # On the first sunday of the month at 8
    scheduler.at(
        scheduler.triggers.time('08:00:00').only_at(
            scheduler.filters.all(
                scheduler.filters.days('1-7'),
                scheduler.filters.weekdays('So'),
            ),
        ),
        my_coro
    )

    # -------------------------------------------------------------------------------------------------------
    # The trigger time can also be modified

    # On sunrise, but not earlier than 8
    scheduler.at(
        scheduler.triggers.sunset().earliest('08:00:00'),
        my_coro
    )

    # One hour before sunset
    scheduler.at(
        scheduler.triggers.sunset().offset(timedelta(hours=-1)),
        my_coro
    )

    # readme example stop
    scheduler._scheduler.remove_all()


@pytest.mark.skipif(os.getenv('TOX_ENV_NAME', '') != '', reason='No run during CI')
def test_sync_example():
    text = Path(__file__).read_text()

    match_example = re.search(r'# readme example start\n(.*)\s+# readme example stop', text, re.DOTALL)
    assert match_example

    pattern_readme = re.compile(r'(## Example\s+````python\n)(.+?)````', re.DOTALL)
    readme_file = Path(__file__).parent.parent / 'README.md'
    readme_text = readme_file.read_text()
    match_readme = pattern_readme.search(readme_text, re.DOTALL)
    assert match_readme

    example_text = dedent(match_example.group(1)).rstrip() + '\n'

    if example_text == match_readme.group(2):
        return None

    readme_new = pattern_readme.sub(match_readme.group(1) + example_text.rstrip(' ') + '````', readme_text)
    assert readme_new != readme_text

    readme_file.write_text(readme_new)
