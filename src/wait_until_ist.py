import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

target_h, target_m = map(int, sys.argv[1].split(":"))
now = datetime.now(ZoneInfo("Asia/Kolkata"))
target = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)

if target < now - timedelta(minutes=5):
    print("Target already passed; continuing immediately.")
    raise SystemExit(0)

seconds = max(0, (target - now).total_seconds())
print(f"Waiting {int(seconds)} seconds for target IST time {target_h:02d}:{target_m:02d}.")
time.sleep(seconds)
