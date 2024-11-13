# EAScheduler
[![Tests Status](https://github.com/spacemanspiff2007/eascheduler/workflows/Tests/badge.svg)](https://github.com/spacemanspiff2007/eascheduler/actions)
[![Documentation Status](https://readthedocs.org/projects/eascheduler/badge/?version=latest)](https://eascheduler.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eascheduler)

[![PyPI](https://img.shields.io/pypi/v/eascheduler)]((https://pypi.org/project/EAScheduler/))
[![Downloads](https://pepy.tech/badge/eascheduler/month)](https://pepy.tech/project/eascheduler)



_Easy async task scheduling_


Easy Async Scheduler (or EAScheduler) is a lightweight asyncio scheduler with a nice and easy to use interface.

The home automation software [HABApp](https://pypi.org/project/HABApp/) make use of EAScheduler.


## Documentation
[The documentation can be found here](https://eascheduler.readthedocs.io)

## Example

````python
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
````

## Changelog

#### 0.1.11 (2023-09-11)
- Fixed an issue with a possible infinite loop

#### 0.1.10 (2023-08-24)
- Added option to add a callback to the job when the execution time changes

#### 0.1.9 (2023-07-19)
- Fix for days when the sun doesn't rise or set.
  In that case the next date with a sunrise/sunset will be returned.

#### 0.1.8 (2022-12-14)
- Fix for OneTimeJob incorrectly showing a remaining time after the execution
- Dependency update

#### 0.1.7 (2022-07-27)
- Added py.typed

#### 0.1.6 (2022-07-27)
- Removed Python 3.7 support
- Fixed setup issues

#### 0.1.5 (2022-02-14)
- Jobs have a remaining function
- CountdownJob has a stop function

#### 0.1.4 (2021-06-01)
- Added option to pause and resume the scheduler
- Jobs don't have to be in the future any more
- Sorted imports with isort

#### 0.1.3 (2021-05-06)
- Fixed a bug where a negative offset/jitter could result in multiple executions

#### 0.1.2 (2021-05-06)
- Fixed a bug where ``.every(None, ...)`` would result in an error

#### 0.1.1 (2021-05-02)
- Implemented a much nicer API and fixed some bugs

#### 0.1.0 (2021-04-21)
- Fixed a race condition
- Added tests

#### 0.0.9 (2021-04-19)
- Fixes for wrong timezone
- Added tests

#### 0.0.8 (2021-04-17)
- Fixes for SunJob, ReoccurringJob
- Added tests

#### 0.0.7 (2021-04-15)
- Fixes for Sunrise/Sunset
