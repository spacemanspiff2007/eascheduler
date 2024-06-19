from datetime import date as dt_date
from typing import Final

from pendulum.tz.local_timezone import get_local_timezone as _local_timezone


local_tz = _local_timezone()


DAY_NAMES: Final[dict[str, int]] = {}


def __create_day_names() -> None:
    values = {}
    for i in range(1, 8):
        values[dt_date(2001, 1, i).strftime('%A').lower()] = i

    values.update({name[:3]: nr for name, nr in values.items()})

    # abbreviations in German and English
    values.update({"mo": 1, "di": 2, "mi": 3, "do": 4, "fr": 5, "sa": 6, "so": 7})
    values.update({"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 7})

    for key, value in sorted(values.items(), key=lambda x: (x[1], x[0])):
        DAY_NAMES[key] = value


__create_day_names()
del __create_day_names
