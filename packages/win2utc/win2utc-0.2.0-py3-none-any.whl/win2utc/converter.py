# win2utc/converter.py

import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # pip install backports.zoneinfo

class WinTimeZoneConverter:
    def __init__(self, tz_json=None, xml_file=None):
        # Load bundled data files unless custom paths are provided
        base = os.path.dirname(os.path.abspath(__file__))
        if tz_json is None:
            tz_json = os.path.join(base, "data", "timezones.json")
        if xml_file is None:
            xml_file = os.path.join(base, "data", "windowsZones.xml")
        with open(tz_json, encoding="utf-8") as f:
            self.timezones = {z['Id']: z for z in json.load(f)}
        self.dotnet_to_iana = self._load_dotnet_to_iana_map(xml_file)

    def _load_dotnet_to_iana_map(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        mapping = {}
        map_timezones = root.find(".//windowsZones/mapTimezones")
        if map_timezones is None:
            raise Exception("Invalid XML structure.")
        for mapzone in map_timezones.findall("mapZone"):
            dotnet = mapzone.attrib["other"]
            if mapzone.attrib["territory"] == "001":
                iana = mapzone.attrib["type"].split()[0]
                mapping[dotnet] = iana
        return mapping

    def _parse_offset(self, offset_str):
        sign = -1 if offset_str.startswith('-') else 1
        h, m, s = map(int, offset_str[1:].split(':'))
        return sign * timedelta(hours=h, minutes=m, seconds=s)

    def to_utc(self, dt, tz_id):
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        note = ""
        iana = self.dotnet_to_iana.get(tz_id)
        if iana:
            try:
                dt_with_tz = dt.replace(tzinfo=ZoneInfo(iana))
                dt_utc = dt_with_tz.astimezone(ZoneInfo("UTC"))
                offset = dt_with_tz.utcoffset()
                note = f"Used IANA mapping '{iana}', full DST support."
                return dt_utc, offset, note
            except Exception as e:
                note = f"Error using zoneinfo: {e}. Fallback to fixed offset."
        tz = self.timezones.get(tz_id)
        if not tz:
            raise ValueError(f"TimeZoneID '{tz_id}' not found!")
        offset = self._parse_offset(tz['BaseUtcOffset'])
        dt_utc = dt - offset
        note = "No IANA mapping found, used fixed offset from timezones.json (no DST)."
        return dt_utc, offset, note
    
    def from_utc(self, dt, tz_id, output_fmt="datetime"):
        """
        Convert UTC datetime to local time in given Windows TimeZoneID.
        dt: str, ISO str, or datetime (UTC)
        tz_id: Windows TimeZoneID
        output_fmt: 'datetime' | 'iso' | 'str'
        Returns: (local_time, offset, note)
        """
        if isinstance(dt, str):
            try:
                # Try ISO first
                dt = datetime.fromisoformat(dt)
            except ValueError:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        note = ""
        iana = self.dotnet_to_iana.get(tz_id)
        if iana:
            try:
                local_dt = dt.astimezone(ZoneInfo(iana))
                offset = local_dt.utcoffset()
                note = f"Used IANA mapping '{iana}', full DST support."
                local_dt_val = local_dt
            except Exception as e:
                note = f"Error using zoneinfo: {e}. Fallback to fixed offset."
                local_dt_val = dt
        else:
            tz = self.timezones.get(tz_id)
            if not tz:
                raise ValueError(f"TimeZoneID '{tz_id}' not found!")
            offset = self._parse_offset(tz['BaseUtcOffset'])
            local_dt_val = dt + offset
            note = "No IANA mapping found, used fixed offset from timezones.json (no DST)."

        # Output format
        if output_fmt == "iso":
            local_dt_val = local_dt_val.isoformat(sep=" ")
        elif output_fmt == "str":
            local_dt_val = local_dt_val.strftime("%Y-%m-%d %H:%M:%S")
        return local_dt_val, offset, note
    
    def range_to_utc(self, start, end, tz_id, input_fmt="str"):
        """
        Convert a local start/end time range in Windows TZ to UTC range.
        Returns: {'gte': utc_start, 'lte': utc_end}
        """
        utc_start, *_ = self.to_utc(start, tz_id)
        utc_end, *_ = self.to_utc(end, tz_id)
        return {'gte': utc_start.strftime("%Y-%m-%d %H:%M:%S"),
                'lte': utc_end.strftime("%Y-%m-%d %H:%M:%S")}

    def iana_to_windows(self, iana_zone):
        """
        Given an IANA timezone name, return the matching Windows TimeZoneID.
        If multiple match, returns the first.
        """
        # Reverse the mapping: IANA → Windows
        rev = {v: k for k, v in self.dotnet_to_iana.items()}
        win_id = rev.get(iana_zone)
        if not win_id:
            raise ValueError(f"No Windows TimeZoneID found for IANA zone '{iana_zone}'")
        return win_id

    def to_utc_df(self, series, tzid, input_fmt="str", output_fmt="str"):
        """
        Convert a pandas Series of datetimes (as string or datetime) to UTC.
        Returns a pandas Series.
        """
        import pandas as pd
        return series.apply(lambda dt: self.to_utc(dt, tzid)[0].strftime("%Y-%m-%d %H:%M:%S")
                            if output_fmt == "str"
                            else self.to_utc(dt, tzid)[0]
        )

    def from_utc_df(self, series, tzid, input_fmt="str", output_fmt="str"):
        """
        Convert a pandas Series of UTC datetimes to local time in Windows TimeZoneID.
        Returns a pandas Series.
        """
        import pandas as pd
        return series.apply(lambda dt: self.from_utc(dt, tzid, output_fmt=output_fmt)[0])

    def list_timezones(self, search=None, iana=False):
        """
        List all supported Windows or IANA timezone names. Optional search filter.
        """
        if iana:
            names = sorted(set(self.dotnet_to_iana.values()))
        else:
            names = sorted(self.timezones.keys())
        if search:
            names = [n for n in names if search.lower() in n.lower()]
        return names

    def get_timezone_info(self, tzid_or_iana):
        """
        Show all info for a given Windows or IANA timezone.
        """
        if tzid_or_iana in self.timezones:
            z = self.timezones[tzid_or_iana]
            return {**z, "IANA": self.dotnet_to_iana.get(tzid_or_iana)}
        else:
            # Try IANA
            win_id = self.iana_to_windows(tzid_or_iana)
            z = self.timezones.get(win_id)
            if z:
                return {**z, "IANA": tzid_or_iana}
        raise ValueError("Timezone not found")
