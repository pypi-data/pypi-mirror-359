# tests/test_converter.py
from win2utc import WinTimeZoneConverter

def test_basic():
    converter = WinTimeZoneConverter()
    dt_str = "2025-07-03 15:00:00"
    tz_id = "Pacific Standard Time"
    utc_dt, offset, note = converter.to_utc(dt_str, tz_id)
    print(utc_dt, offset, note)
    assert utc_dt.strftime("%Y-%m-%d %H:%M:%S") == "2025-07-03 22:00:00"  # This is for illustration!

if __name__ == "__main__":
    test_basic()
