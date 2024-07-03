# EAScheduler
[![Tests Status](https://github.com/spacemanspiff2007/eascheduler/workflows/Tests/badge.svg)](https://github.com/spacemanspiff2007/eascheduler/actions)
[![Documentation Status](https://readthedocs.org/projects/eascheduler/badge/?version=latest)](https://eascheduler.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eascheduler)

[![PyPI](https://img.shields.io/pypi/v/eascheduler)]((https://pypi.org/project/EAScheduler/))
[![Downloads](https://pepy.tech/badge/eascheduler/month)](https://pepy.tech/project/eascheduler)



_Easy async task scheduling_


Easy Async Scheduler (or EAScheduler) is a lightweight asyncio scheduler with a nice and easy to use interface.

## Documentation
[The documentation can be found at here](https://eascheduler.readthedocs.io)

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
