from eascheduler.builder.helper import HINT_INSTANT, get_instant
from eascheduler.producers.prod_sun import get_azimuth_and_elevation


def get_sun_position(instant: HINT_INSTANT) -> tuple[float, float]:
    """Return the sun position (azimuth and elevation) at a given instant.

    :param instant: instant to get the sun position at or None for now
    :return: azimuth and elevation of the sun at the specified instant
    """
    return get_azimuth_and_elevation(get_instant(instant))
