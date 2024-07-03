from whenever import LocalSystemDateTime, UTCDateTime, ZonedDateTime


def get_local_as_utc(month=1, day=1, hour=0, minute=0, second=0, *, year=2001,) -> UTCDateTime:
    return LocalSystemDateTime(year, month, day, hour, minute=minute, second=second).as_utc()


def get_local_as_utc(month=1, day=1, hour=0, minute=0, second=0, *, year=2001, microsecond=0) -> UTCDateTime:
    return ZonedDateTime(
        year, month, day, hour, minute=minute, second=second, microsecond=microsecond, tz='Europe/Berlin').as_utc()


def cmp_utc_with_local(obj, *args, **kwargs):
    from_local = get_local_as_utc(*args, **kwargs)
    assert obj == from_local, f"\n{obj}\n{from_local}"
    return obj == from_local


def cmp_utc_with_german(obj, *args, **kwargs):
    from_german = get_local_as_utc(*args, **kwargs)
    assert obj == from_german, f"\n{obj}\n{from_german}"
    return obj == from_german


def get_ger_str(obj: UTCDateTime) -> str:
    return obj.as_zoned('Europe/Berlin').as_offset().common_iso8601()
