# win2utc/cli.py

import argparse
from .converter import WinTimeZoneConverter
import sys

def main():
    parser = argparse.ArgumentParser(description="Convert datetimes between Windows TimeZone and UTC.")
    parser.add_argument("--range", nargs=3, metavar=("START", "END", "TZID"), help="Convert a local time range to UTC.")
    parser.add_argument("--from-utc", action="store_true", help="Convert from UTC to local.")
    parser.add_argument("--fmt", default="str", choices=["str", "iso", "datetime"], help="Output format.")
    parser.add_argument("dt", nargs="?", help="Datetime string (local or UTC).")
    parser.add_argument("tzid", nargs="?", help="Windows TimeZoneID (e.g. 'Pacific Standard Time')")
    args = parser.parse_args()

    converter = WinTimeZoneConverter()

    if args.range:
        start, end, tzid = args.range
        utc_range = converter.range_to_utc(start, end, tzid)
        print("UTC range:", utc_range)
    elif args.dt and args.tzid:
        if args.from_utc:
            local, offset, note = converter.from_utc(args.dt, args.tzid, output_fmt=args.fmt)
            print(f"Local: {local} (offset={offset})\nNote: {note}")
        else:
            utc, offset, note = converter.to_utc(args.dt, args.tzid)
            if args.fmt == "iso":
                utc = utc.isoformat(sep=" ")
            elif args.fmt == "str":
                utc = utc.strftime("%Y-%m-%d %H:%M:%S")
            print(f"UTC: {utc} (offset={offset})\nNote: {note}")
    else:
        parser.print_help()
        sys.exit(1)
