import json
from pathlib import Path

from brand import BACKGROUND_LABELS

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"
MILO_LIBRARY = ROOT / "assets" / "milo_library"

VALID_CAPTION_CATEGORIES = {
    "marriage", "it", "meetings", "manager", "salary",
    "wife", "husband", "sister", "brother", "driving",
}
VALID_MUSIC_CATEGORIES = {
    "general", "work", "money", "relationship", "family", "driving",
}


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
        assert row["quote_position"] == "upper_center", (
            f"Month 1 quote must use locked upper-center placement: day {row['day']}"
        )
        assert row["caption_category"] in VALID_CAPTION_CATEGORIES, (
            f"Invalid caption category: {row['caption_category']}"
        )
        assert row["music_category"] in VALID_MUSIC_CATEGORIES, (
            f"Invalid music category: {row['music_category']}"
        )

        illustration = MILO_LIBRARY / row["illustration"]
        assert illustration.exists(), (
            f"Mapped Milo illustration does not exist for day {row['day']}: "
            f"{row['illustration']}"
        )
        assert illustration.suffix.lower() == ".png", (
            f"Milo illustration must be PNG: {row['illustration']}"
        )

        dates.add(row["date"])
        quotes.add(row["quote"].lower())

    print(
        "Campaign gate passed: 30 unique final quotes, locked backgrounds, "
        "centered typography, caption/music categories and Milo mappings are valid."
    )


if __name__ == "__main__":
    main()
