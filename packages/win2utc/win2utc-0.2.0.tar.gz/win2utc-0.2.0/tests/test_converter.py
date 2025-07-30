from win2utc import WinTimeZoneConverter

def test_to_utc():
    c = WinTimeZoneConverter()
    dt, offset, note = c.to_utc("2025-11-01 10:00:00", "Pacific Standard Time")
    print(dt, offset, note)
    assert dt.strftime("%Y-%m-%d %H:%M:%S") == "2025-11-01 17:00:00"

def test_from_utc():
    c = WinTimeZoneConverter()
    local, offset, note = c.from_utc("2025-11-01 17:00:00", "Pacific Standard Time", output_fmt="str")
    print(local, offset, note)
    assert local == "2025-11-01 10:00:00"

def test_range_to_utc():
    c = WinTimeZoneConverter()
    rng = c.range_to_utc("2025-11-01 00:00:00", "2025-11-01 23:59:59", "Pacific Standard Time")
    print(rng)
    assert rng['gte'] == "2025-11-01 07:00:00"
    assert rng['lte'] == "2025-11-02 06:59:59"

def test_iana_to_windows():
    c = WinTimeZoneConverter()
    win = c.iana_to_windows("America/New_York")
    print("America/New_York ->", win)
    assert win == "Eastern Standard Time"

def test_to_utc_df():
    import pandas as pd
    c = WinTimeZoneConverter()
    df = pd.DataFrame({
        "local_time": ["2025-07-03 10:00:00", "2025-07-03 22:00:00"]
    })
    df['utc_time'] = c.to_utc_df(df['local_time'], "Eastern Standard Time")
    print(df)
    assert df['utc_time'].iloc[0] == "2025-07-03 14:00:00"

def test_list_timezones():
    c = WinTimeZoneConverter()
    win_zones = c.list_timezones(search="Pacific")
    iana_zones = c.list_timezones(iana=True, search="Los")
    print("Windows:", win_zones)
    print("IANA:", iana_zones)
    assert "Pacific Standard Time" in win_zones
    assert "America/Los_Angeles" in iana_zones

def test_get_timezone_info():
    c = WinTimeZoneConverter()
    info = c.get_timezone_info("Pacific Standard Time")
    print(info)
    assert info["Id"] == "Pacific Standard Time"
    info2 = c.get_timezone_info("America/Los_Angeles")
    print(info2)
    assert info2["IANA"] == "America/Los_Angeles"

if __name__ == "__main__":
    test_to_utc()
    test_from_utc()
    test_range_to_utc()
    test_iana_to_windows()
    test_to_utc_df()
    test_list_timezones()
    test_get_timezone_info()
    print("All tests passed!")
