.. |param_scheduled_cb| replace:: Function which will be called
.. |param_scheduled_cb_args| replace:: Positional arguments that will be passed to the coroutine function
.. |param_scheduled_cb_kwargs| replace:: Keyword arguments that will be passed to the coroutine function
.. |param_job_id| replace:: Job id to manually identify the job


API Docs
==================================

Builders
----------------------------------

.. py:currentmodule:: eascheduler.builder

Builders help to create complex objects in a more readable and convenient way.

.. autoclass:: JobBuilder
   :members:
   :inherited-members:

.. autoclass:: TriggerBuilder
   :members:
   :inherited-members:

.. autoclass:: FilterBuilder
   :members:
   :inherited-members:


Job Control
----------------------------------

.. py:currentmodule:: eascheduler.job_control


.. autoclass:: OneTimeJobControl
   :members:
   :inherited-members:

.. autoclass:: CountdownJobControl
   :members:
   :inherited-members:

.. autoclass:: DateTimeJobControl
   :members:
   :inherited-members:


Exception Handling
----------------------------------

.. autofunction:: eascheduler.set_exception_handler


Sun Position
----------------------------------

.. autofunction:: eascheduler.set_location

.. autofunction:: eascheduler.get_sun_position


Holidays
----------------------------------

.. autofunction:: eascheduler.setup_holidays

.. autofunction:: eascheduler.add_holiday

.. autofunction:: eascheduler.get_holiday_name

.. autofunction:: eascheduler.get_holidays_by_name

.. autofunction:: eascheduler.is_holiday

.. autofunction:: eascheduler.pop_holiday


TriggerObject
----------------------------------

.. autoclass:: eascheduler.builder.triggers.TriggerObject
   :members:



Job status
----------------------------------

.. autoclass:: eascheduler.jobs.base.JobStatusEnum
   :members:


Task Managers
----------------------------------

Parallel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:currentmodule:: eascheduler.task_managers


.. autoclass:: ParallelTaskManager
   :members:


.. autoclass:: LimitingParallelTaskManager
   :members:
   :special-members: __init__


Sequential
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:currentmodule:: eascheduler.task_managers


.. autoclass:: SequentialTaskManager
   :members:


.. autoclass:: LimitingSequentialTaskManager
   :members:
   :special-members: __init__


.. autoclass:: SequentialDeduplicatingTaskManager
   :members:
