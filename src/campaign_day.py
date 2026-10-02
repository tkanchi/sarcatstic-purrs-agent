import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"

rows = json.loads(CONTENT.read_text(encoding="utf-8"))
override = os.getenv("DAY_NUMBER", "").strip()

if override:
    day = int(override)
    if not 1 <= day <= 30:
        raise ValueError("DAY_NUMBER must be between 1 and 30")
else:
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    matches = [row for row in rows if row["date"] == today]
    if not matches:
        print("0")
        raise SystemExit(0)
    day = matches[0]["day"]

print(day)
