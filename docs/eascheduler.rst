About
==================================
EAScheduler is a easy-to-use, lightweight yet very powerful asyncio scheduler for Python.


Getting Started
==================================

While EAScheduler is very flexible and you can tailor it to your needs,
it also comes with a default scheduler that you can use out of the box.


.. exec_code::
   :hide_output:

   import asyncio
   import eascheduler

   async def my_asyncio_code():

      # If you want something easy that you can use out of the box just use the default scheduler
      scheduler = eascheduler.get_default_scheduler()

      # Define a coroutine that should be executed
      async def my_coro():
          print('Hello')

      # -------------------------------------------------------------------------------------------------------
      # A Job that runs only once, e.g.
      # this job will run in 30 seconds
      job_once = scheduler.once(30, my_coro)

      # -------------------------------------------------------------------------------------------------------
      # Countdown job which can be stopped and started again
      countdown = scheduler.countdown(30, my_coro)
      countdown.reset()               # make countdown start (again)
      countdown.stop()                # stop countdown
      countdown.set_countdown(15)     # set different countdown time which will be used
                                      # for the next reset call

      # -------------------------------------------------------------------------------------------------------
      # Jobs with a trigger job which runs continuously
      # The trigger describes the reoccurring execution time of the job

      # this job will run every day at 8
      job_every = scheduler.at(scheduler.triggers.time('08:00:00'), my_coro)

      # this job will run for the first time in 10 min, then every hour
      job_every = scheduler.at(scheduler.triggers.interval(600, 3600), my_coro)


   asyncio.run(my_asyncio_code())


Passing arguments to the coroutine function
===========================================

It's possible to pass both arguments and keyword arguments to the coroutine function.


.. exec_code::

   # --- hide: start -----
   import asyncio
   import eascheduler
   eascheduler.set_location(52.51870, 13.37607)

   async def my_asyncio_code():

      scheduler = eascheduler.get_default_scheduler()
   # --- hide: stop -----

      async def my_coro(a, b=None, c=None):
          print(f'a: {a}, b: {b}, c: {c}')

      # Scheduling a onetime job with None means it will run as soon as possible
      job_every = scheduler.once(None, my_coro, 'a1', c='kw1')

   # --- hide: start -----
      await asyncio.sleep(0.1)

   asyncio.run(my_asyncio_code())

Reoccurring Jobs
==================================

All triggers, filters and processing of triggers are immutable and can be composed without side effects.


Grouping triggers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's possible to group triggers to create more complex schedules.


.. exec_code::
   :hide_output:

   # --- hide: start -----
   import asyncio
   import eascheduler
   eascheduler.set_location(52.51870, 13.37607)

   async def my_asyncio_code():

      scheduler = eascheduler.get_default_scheduler()
      async def my_coro():
          print('Hello')
   # --- hide: stop -----

      # This job will run every day at sunrise and at 12
      job_every = scheduler.at(
         scheduler.triggers.group(
            scheduler.triggers.sunrise(),
            scheduler.triggers.time('12:00:00')
         ),
         my_coro
      )

   # --- hide: start -----
   asyncio.run(my_asyncio_code())


Processing triggers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The time of a trigger can be further processed

.. exec_code::
   :hide_output:

   # --- hide: start -----
   import asyncio
   import eascheduler
   eascheduler.set_location(52.51870, 13.37607)

   async def my_asyncio_code():

      scheduler = eascheduler.get_default_scheduler()
      async def my_coro():
          print('Hello')
   # --- hide: stop -----

      # One hour after sunrise
      job_every = scheduler.at(
         scheduler.triggers.sunrise().offset(3600),
         my_coro
      )

      # On sunrise but not before 7:30
      job_every = scheduler.at(
         scheduler.triggers.sunrise().earliest('07:30:00'),
         my_coro
      )

   # --- hide: start -----
   asyncio.run(my_asyncio_code())


Filtering triggers
==================================

It's possible to filter triggers. When the filter condition is true the trigger time will be used

.. exec_code::
   :hide_output:

   # --- hide: start -----
   import asyncio
   import eascheduler
   eascheduler.set_location(52.51870, 13.37607)

   async def my_asyncio_code():

      scheduler = eascheduler.get_default_scheduler()
      async def my_coro():
          print('Hello')
   # --- hide: stop -----

      # Every Fr-So at 8
      job_every = scheduler.at(
         scheduler.triggers.time('08:00:00').only_at(scheduler.filters.weekdays('Fr-So')),
         my_coro
      )

      # At 1 every first day of the month
      job_every = scheduler.at(
         scheduler.triggers.time('01:00:00').only_at(scheduler.filters.days('1')),
         my_coro
      )


   # --- hide: start -----
   asyncio.run(my_asyncio_code())



Filters can also be grouped. Combining them with :meth:`~eascheduler.builder.FilterBuilder.all` requires all filters to pass,
combining them with :meth:`~eascheduler.builder.FilterBuilder.any` requires at least one filter to pass.
Filters can also be inverted with :meth:`~eascheduler.builder.FilterBuilder.not_`.

.. exec_code::
   :hide_output:

   # --- hide: start -----
   import asyncio
   import eascheduler
   eascheduler.set_location(52.51870, 13.37607)

   async def my_asyncio_code():

      scheduler = eascheduler.get_default_scheduler()
      async def my_coro():
          print('Hello')
   # --- hide: stop -----

      # On the first sunday of the month at 08:00
      job_every = scheduler.at(
         scheduler.triggers.time('08:00:00').only_at(
            scheduler.filters.all(
               scheduler.filters.days('1-7'),
               scheduler.filters.weekdays('So'),
            )
         ),
         my_coro
      )

      # On the first of every month at 08:00 and on every sunday at 08:00
      job_every = scheduler.at(
         scheduler.triggers.time('08:00:00').only_at(
            scheduler.filters.any(
               scheduler.filters.days(1),
               scheduler.filters.weekdays('So'),
            )
         ),
         my_coro
      )


   # --- hide: start -----
   asyncio.run(my_asyncio_code())


Setting up EAScheduler
==================================
Some functionalities of EAScheduler require a bit of setup.
If sun functionalities should be used :func:`~eascheduler.set_location` needs to be called first.
For holidays :func:`~eascheduler.setup_holidays` is required and a custom exception handler can be set with
:func:`~eascheduler.set_exception_handler`


.. exec_code::
   :hide_output:

   import eascheduler

   # The sun triggers need the location
   eascheduler.set_location(52.51870, 13.37607)

   # The holiday triggers need the country code and optionally the subdivision code
   # Here the country is Germany and the subdivision is Berlin
   eascheduler.setup_holidays('DE', 'BE')

   # Is possible to register a custom exception handler that gets called when an error occurs
   # The default exception handler will just log the errors with the logging module
   def my_exception_handler(e: Exception):
      print(f'Exception occurred: {e}')

   eascheduler.set_exception_handler(my_exception_handler)


Other functions
==================================


.. list-table::
   :widths: auto
   :header-rows: 1

   * - Sun related functions

   * - :func:`eascheduler.set_location`

   * - :func:`eascheduler.get_sun_position`


.. list-table::
   :widths: auto
   :header-rows: 1

   * - Holiday related functions

   * - :func:`eascheduler.setup_holidays`

   * - :func:`eascheduler.add_holiday`

   * - :func:`eascheduler.get_holiday_name`

   * - :func:`eascheduler.get_holidays_by_name`

   * - :func:`eascheduler.is_holiday`

   * - :func:`eascheduler.pop_holiday`


.. list-table::
   :widths: auto
   :header-rows: 1

   * - Exception Handling

   * - :func:`eascheduler.set_exception_handler`
