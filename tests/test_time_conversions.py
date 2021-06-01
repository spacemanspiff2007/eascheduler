from datetime import datetime

import pytest
from pendulum import DateTime, from_timestamp, instance, UTC

from eascheduler.const import local_tz

berlin_tz = str(local_tz) == "Timezone('Europe/Berlin')"


@pytest.mark.skipif(not berlin_tz, reason='Test only works in time zone Europe/Berlin')
def test_to_timestamp():
    # Timestamps are always in UTC
    assert DateTime(2001, 1, 1, 12, tzinfo=local_tz).timestamp() == 978346800
    assert DateTime(2001, 1, 1, 11, tzinfo=UTC).timestamp()      == 978346800


@pytest.mark.skipif(not berlin_tz, reason='Test only works in time zone Europe/Berlin')
def test_from_timestamp():
    # Loading from timestamps always works correct
    assert from_timestamp(978346800, tz=local_tz) == DateTime(2001, 1, 1, 12, tzinfo=local_tz)
    assert from_timestamp(978346800, tz=UTC)      == DateTime(2001, 1, 1, 11, tzinfo=UTC)


@pytest.mark.skipif(not berlin_tz, reason='Test only works in time zone Europe/Berlin')
def test_from_instance():
    dt = datetime(2001, 1, 1, 12)

    # creating a DateTime from dt works like this
    aware_obj = instance(dt, tz=local_tz)
    assert aware_obj == DateTime(2001, 1, 1, 12, tzinfo=local_tz)
    assert aware_obj.naive() == dt

    # back and forth conversation from naive to aware
    naive = DateTime(2001, 1, 1, 11, tzinfo=UTC).in_timezone(local_tz).naive()
    assert naive == DateTime(2001, 1, 1, 12)
    aware = instance(naive, local_tz).astimezone(local_tz)
    assert aware == DateTime(2001, 1, 1, 12, tzinfo=local_tz)

    # creating a DateTime from dt works like this
    aware = instance(dt, local_tz).astimezone(local_tz)
    assert aware == DateTime(2001, 1, 1, 12, tzinfo=local_tz)
