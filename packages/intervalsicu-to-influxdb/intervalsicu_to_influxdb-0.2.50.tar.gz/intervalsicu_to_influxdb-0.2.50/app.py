import argparse

from src.intervalsicu_to_influxdb.extractor import IntervalsToInflux

# Arg parser
parser = argparse.ArgumentParser()

parser.add_argument("--date", type=str, help="Date in format YYYY-MM-DD")
parser.add_argument("--start-date", type=str, help="Start date in format YYYY-MM-DD")
parser.add_argument("--end-date", type=str, help="End date in format YYYY-MM-DD")
parser.add_argument(
    "--streams",
    action="store_true",
    help="Export streams for the activities",
)
parser.add_argument(
    "--reset", action="store_true", help="Reset influx bucket (delete and create)"
)

args = parser.parse_args()

if args.date:
    date = args.date
else:
    date = None
if args.start_date:
    start_date = args.start_date
else:
    start_date = None
if args.end_date:
    end_date = args.end_date
else:
    end_date = None
if args.streams:
    streams = True
else:
    streams = False
if args.reset:
    reset = True
else:
    reset = False

extractor = IntervalsToInflux(date, start_date, end_date, reset, streams)
extractor.all_data()
