from linkpulse.utilities import utc_now


def test_utcnow_tz_aware():
    dt = utc_now()
    dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None
