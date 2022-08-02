# EAScheduler
[![Tests Status](https://github.com/spacemanspiff2007/eascheduler/workflows/Tests/badge.svg)](https://github.com/spacemanspiff2007/eascheduler/actions)
[![Documentation Status](https://readthedocs.org/projects/eascheduler/badge/?version=latest)](https://eascheduler.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/eascheduler/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eascheduler)

[![PyPI](https://img.shields.io/pypi/v/eascheduler)]((https://pypi.org/project/EAScheduler/))
[![Downloads](https://pepy.tech/badge/eascheduler/month)](https://pepy.tech/project/eascheduler/month)



_Easy async task scheduling_


Easy Async Scheduler (or EAScheduler) is a lightweight asyncio scheduler with a nice and easy to use interface.

## Documentation
[The documentation can be found at here](https://eascheduler.readthedocs.io)

## Changelog

#### 0.1.7 (27.07.2022)
- Added py.typed

#### 0.1.6 (27.07.2022)
- Removed Python 3.7 support
- Fixed setup issues

#### 0.1.5 (14.02.2022)
- Jobs have a remaining function
- CountdownJob has a stop function

#### 0.1.4 (01.06.2021)
- Added option to pause and resume the scheduler
- Jobs don't have to be in the future any more
- Sorted imports with isort

#### 0.1.3 (06.05.2021)
- Fixed a bug where a negative offset/jitter could result in multiple executions

#### 0.1.2 (06.05.2021)
- Fixed a bug where ``.every(None, ...)`` would result in an error

#### 0.1.1 (02.05.2021)
- Implemented a much nicer API and fixed some bugs

#### 0.1.0 (21.04.2021)
- Fixed a race condition
- Added tests

#### 0.0.9 (19.04.2021)
- Fixes for wrong timezone
- Added tests

#### 0.0.8 (17.04.2021)
- Fixes for SunJob, ReoccurringJob
- Added tests

#### 0.0.7 (15.04.2021)
- Fixes for Sunrise/Sunset
