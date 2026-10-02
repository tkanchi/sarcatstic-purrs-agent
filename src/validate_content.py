import json
from pathlib import Path
from brand import BACKGROUND_LABELS

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"

def main():
    rows = json.loads(CONTENT.read_text(encoding="utf-8"))
    assert len(rows) == 30, f"Expected exactly 30 posts, found {len(rows)}"
    dates = set()
    quotes = set()

    for expected_day, row in enumerate(rows, start=1):
        assert row["day"] == expected_day, f"Unexpected day number: {row}"
        assert row["date"] not in dates, f"Duplicate date: {row['date']}"
        assert row["quote"].lower() not in quotes, f"Duplicate quote: {row['quote']}"
        assert row["background"] in BACKGROUND_LABELS, f"Invalid background: {row['background']}"
        assert len(row["quote"]) <= 80, f"Quote too long: {row['quote']}"
        assert row["quote_position"] in {"upper_left", "upper_center"}
        dates.add(row["date"])
        quotes.add(row["quote"].lower())

    print("Brand/content gate passed: 30 unique posts, valid backgrounds, quote length <= 80.")

if __name__ == "__main__":
    main()
