from enum import Enum

from pendulum import now as __now
from pendulum.tz.local_timezone import get_local_timezone as _local_timezone

local_tz = _local_timezone()

# Let's just hope they fixed the timestamp overflow till 2038 ;-)
FAR_FUTURE: float = float(2**(31 if __now().year < 2038 else 33) - 1)


class _Execution(Enum):
    SKIP = object()

    def __str__(self):
        return f'<{self.name}_EXECUTION>'


SKIP_EXECUTION = _Execution.SKIP
