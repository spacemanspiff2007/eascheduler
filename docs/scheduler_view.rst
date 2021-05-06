.. |param_scheduled_cb| replace:: Function which will be called
.. |param_scheduled_cb_args| replace:: Positional arguments that will be passed to the function
.. |param_scheduled_cb_kwargs| replace:: Keyword arguments that will be passed to the function


**************************************
Easy Async Scheduler
**************************************

Interaction
======================================

SchedulerView
--------------------------------------

.. autoclass:: eascheduler.SchedulerView
   :members:
   :inherited-members:

Jobs
======================================

DayOfWeekJob
--------------------------------------

.. autoclass:: eascheduler.jobs.DayOfWeekJob
   :members:
   :inherited-members:

ExpiringJob
--------------------------------------

.. autoclass:: eascheduler.jobs.CountdownJob
   :members:
   :inherited-members:

OneTimeJob
--------------------------------------

.. autoclass:: eascheduler.jobs.OneTimeJob
   :members:
   :inherited-members:

ReoccurringJob
--------------------------------------

.. autoclass:: eascheduler.jobs.ReoccurringJob
   :members:
   :inherited-members:
