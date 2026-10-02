import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"

KEYWORDS = {
    "work": "work humor, office life, meetings, corporate life, relatable humor",
    "social": "social battery, introvert humor, people, relatable sarcasm, cat humor",
    "relationships": "relationship humor, texting, boundaries, relatable sarcasm, cat humor",
    "overthinking": "overthinking, anxious thoughts, relatable humor, daily life, cat humor",
    "productivity": "productivity humor, motivation, procrastination, daily life, cat humor",
    "adulting": "adulting, everyday life, relatable humor, sarcasm, cat humor",
    "mood": "mood, relatable humor, sarcasm, everyday life, cat humor",
    "everyday": "everyday life, relatable humor, sarcasm, funny cat, cat humor",
}

def get_post(day):
    rows = json.loads(CONTENT.read_text(encoding="utf-8"))
    return next(row for row in rows if row["day"] == day)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--output", default="outputs/caption.txt")
    args = parser.parse_args()

    post = get_post(args.day)
    keywords = KEYWORDS.get(post["pillar"], KEYWORDS["everyday"])
    caption = (
        "Send this to the friend who would understand Milo immediately. 😼\n\n"
        "Read the whole line before pretending it isn’t you. "
        f"{keywords}.\n\n"
        "Follow SARCATSTIC PURRS for more Milo-level honesty — and share it with someone who needs the laugh."
    )

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(caption, encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
