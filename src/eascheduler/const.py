from datetime import date as dt_date
from datetime import datetime, tzinfo
from typing import Final, Iterable


local_tz: Final[tzinfo] = datetime.now().astimezone().tzinfo


DAY_NAMES: Final[dict[str, int]] = {}
MONTH_NAMES: Final[dict[str, int]] = {}


def __create_day_names() -> None:
    values = {}

    def add_values(objs: Iterable[str], cut: int | None):
        for i, day in enumerate(objs, start=1):
            values[day.lower()] = i
            if cut:
                values[day[:cut].lower()] = i

    def to_dict(dst: dict):
        for key, value in sorted(values.items(), key=lambda x: (x[1], x[0])):
            dst[key] = value

    for i in range(1, 8):
        values[dt_date(2001, 1, i).strftime('%A').lower()] = i
        values[dt_date(2001, 1, i).strftime('%a').lower()] = i

    add_values(['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], 2)
    add_values(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 3)

    to_dict(DAY_NAMES)

    # Months
    values = {}
    for i in range(1, 13):
        values[dt_date(2001, i, 1).strftime('%B').lower()] = i
        values[dt_date(2001, i, 1).strftime('%b').lower()] = i

    add_values(['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober',
                'November', 'Dezember'], 3)
    values['mrz'] = 3

    add_values(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                'November', 'December'], 3)

    to_dict(MONTH_NAMES)


__create_day_names()
del __create_day_names
