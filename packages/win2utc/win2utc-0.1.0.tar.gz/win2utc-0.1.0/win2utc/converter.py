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
