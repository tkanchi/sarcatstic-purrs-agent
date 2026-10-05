import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"
PUBLISHED_LOGS = ROOT / "published_logs"

rows = json.loads(CONTENT.read_text(encoding="utf-8"))
override = os.getenv("DAY_NUMBER", "").strip()

if override:
    # Manual runs may target any specific campaign day.
    day = int(override)
    if not 1 <= day <= len(rows):
        raise ValueError(f"DAY_NUMBER must be between 1 and {len(rows)}")
    print(day)
    raise SystemExit(0)

# Scheduled mode: exactly one new Reel per India calendar day.
today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
published_days = set()
published_today = False

if PUBLISHED_LOGS.exists():
    for path in PUBLISHED_LOGS.glob("day_*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if payload.get("status") != "PUBLISHED":
            continue

        try:
            published_days.add(int(path.stem.split("_", 1)[1]))
        except (IndexError, ValueError):
            pass

        if payload.get("published_date_ist") == today_ist:
            published_today = True

if published_today:
    print("0")
    raise SystemExit(0)

# Pick the first approved quote that has never been published.
for row in rows:
    if row["day"] not in published_days:
        print(row["day"])
        raise SystemExit(0)

# Nothing left in the current approved bank.
print("0")
