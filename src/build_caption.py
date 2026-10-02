import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "month_01.json"

CATEGORY_ALIASES = {
    "work": "work",
    "it": "it",
    "it_job": "it",
    "meeting": "meetings",
    "meetings": "meetings",
    "manager": "manager",
    "money": "salary",
    "salary": "salary",
    "relationship": "relationships",
    "relationships": "relationships",
    "marriage": "marriage",
    "wife": "wife",
    "husband": "husband",
    "family": "family",
    "sister": "sister",
    "brother": "brother",
    "driving": "driving",
    "traffic": "driving",
    "general": "general",
    "everyday": "general",
    "social": "general",
    "mood": "general",
    "adulting": "general",
    "productivity": "general",
    "overthinking": "general",
}

CONFIG = {
    "marriage": {
        "keywords": (
            "marriage humor, married life, husband wife jokes, couple humor, "
            "relationship memes, funny marriage moments, relatable relationship humor, "
            "sarcastic humor, funny cat reels and everyday couple struggles"
        ),
        "hashtags": [
            "#MarriageHumor",
            "#CoupleHumor",
            "#RelationshipHumor",
            "#RelatableReels",
            "#FunnyReels",
        ],
    },
    "it": {
        "keywords": (
            "IT humor, tech humor, software life, developer jokes, office humor, "
            "corporate life, bug fixing, laptop life, work memes, relatable work humor, "
            "sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#ITHumor",
            "#TechHumor",
            "#WorkHumor",
            "#OfficeHumor",
            "#RelatableReels",
        ],
    },
    "meetings": {
        "keywords": (
            "meeting humor, office meetings, corporate meetings, Zoom calls, Teams calls, "
            "workplace comedy, corporate life, meeting memes, office jokes, relatable work humor, "
            "sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#MeetingHumor",
            "#OfficeHumor",
            "#CorporateHumor",
            "#WorkMemes",
            "#RelatableReels",
        ],
    },
    "manager": {
        "keywords": (
            "manager humor, boss jokes, office life, corporate humor, workplace comedy, "
            "deadlines, quick tasks, status updates, work memes, relatable work humor, "
            "sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#ManagerHumor",
            "#OfficeHumor",
            "#CorporateLife",
            "#WorkMemes",
            "#RelatableReels",
        ],
    },
    "salary": {
        "keywords": (
            "salary humor, payday jokes, bank balance humor, bills, adulting humor, "
            "office life, work memes, money struggles, relatable humor, sarcastic humor, "
            "funny cat reels and everyday life memes"
        ),
        "hashtags": [
            "#SalaryHumor",
            "#PaydayHumor",
            "#AdultingHumor",
            "#WorkHumor",
            "#RelatableReels",
        ],
    },
    "wife": {
        "keywords": (
            "wife humor, marriage humor, husband wife jokes, married life, couple humor, "
            "relationship memes, funny marriage moments, relatable relationship humor, "
            "sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#WifeHumor",
            "#MarriageHumor",
            "#CoupleHumor",
            "#RelationshipHumor",
            "#RelatableReels",
        ],
    },
    "husband": {
        "keywords": (
            "husband humor, marriage humor, husband wife jokes, married life, couple humor, "
            "relationship memes, funny husband moments, relatable relationship humor, "
            "sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#HusbandHumor",
            "#MarriageHumor",
            "#CoupleHumor",
            "#RelationshipHumor",
            "#RelatableReels",
        ],
    },
    "sister": {
        "keywords": (
            "sister humor, sibling jokes, sister memes, family humor, sibling rivalry, "
            "funny family moments, relatable sibling humor, everyday sarcasm, "
            "funny cat reels and relatable memes"
        ),
        "hashtags": [
            "#SisterHumor",
            "#SiblingHumor",
            "#FamilyHumor",
            "#RelatableReels",
            "#FunnyReels",
        ],
    },
    "brother": {
        "keywords": (
            "brother humor, sibling jokes, brother memes, family humor, sibling rivalry, "
            "funny family moments, relatable sibling humor, everyday sarcasm, "
            "funny cat reels and relatable memes"
        ),
        "hashtags": [
            "#BrotherHumor",
            "#SiblingHumor",
            "#FamilyHumor",
            "#RelatableReels",
            "#FunnyReels",
        ],
    },
    "driving": {
        "keywords": (
            "driving humor, traffic jokes, road rage humor, daily commute, bad drivers, "
            "traffic memes, car humor, relatable driving moments, everyday sarcasm, "
            "funny cat reels and relatable memes"
        ),
        "hashtags": [
            "#DrivingHumor",
            "#TrafficHumor",
            "#RoadRage",
            "#RelatableReels",
            "#FunnyReels",
        ],
    },
    "relationships": {
        "keywords": (
            "relationship humor, couple jokes, married life, dating humor, everyday relationships, "
            "relatable memes, sarcastic humor, funny cat reels and real life comedy"
        ),
        "hashtags": [
            "#RelationshipHumor",
            "#CoupleHumor",
            "#RelatableHumor",
            "#FunnyReels",
            "#RelatableReels",
        ],
    },
    "family": {
        "keywords": (
            "family humor, sibling jokes, family memes, relatable family moments, "
            "everyday sarcasm, funny cat reels, relatable memes and daily life humor"
        ),
        "hashtags": [
            "#FamilyHumor",
            "#SiblingHumor",
            "#RelatableHumor",
            "#FunnyReels",
            "#RelatableReels",
        ],
    },
    "work": {
        "keywords": (
            "work humor, office life, corporate humor, meetings, managers, workplace comedy, "
            "work memes, relatable work moments, sarcastic humor and funny cat reels"
        ),
        "hashtags": [
            "#WorkHumor",
            "#OfficeHumor",
            "#CorporateHumor",
            "#WorkMemes",
            "#RelatableReels",
        ],
    },
    "general": {
        "keywords": (
            "relatable humor, sarcastic humor, funny cat reels, cat memes, everyday life, "
            "daily sarcasm, introvert humor, funny reactions, relatable memes and comedy reels"
        ),
        "hashtags": [
            "#RelatableHumor",
            "#SarcasticHumor",
            "#CatMemes",
            "#FunnyReels",
            "#RelatableReels",
        ],
    },
}

HOOKS = [
    "Send this to the one person who will feel personally attacked by this. 😼😂",
    "Tag the friend who would read this and immediately say, ‘That’s me.’ 😹",
    "Share this with someone whose life is basically this joke. 😼",
    "Send this to the person who needs this very specific Milo-level reality check. 😂🐾",
]

READ_CTA = [
    "Read the whole line — the last part is where Milo usually gets too accurate.",
    "Watch till the end and tell me this isn’t painfully relatable.",
    "Don’t scroll too fast. Milo has already judged the situation for you.",
    "Read it twice. It somehow gets more personal the second time.",
]

FOLLOW_CTA = [
    "Save it for later, share it with your people, and follow for more daily Milo sarcasm. 🐾",
    "Save this one, send it to a friend, and follow for more relatable Milo chaos. 😼",
    "If this felt a little too accurate, save it and follow for more Milo-level honesty. 🐾",
    "Share the laugh, save the Reel, and follow for more sarcastic cat humor every day. 😹",
]


def get_post(day):
    rows = json.loads(CONTENT.read_text(encoding="utf-8"))
    return next(row for row in rows if row["day"] == day)


def category_for(post):
    raw = (
        post.get("caption_category")
        or post.get("category")
        or post.get("pillar")
        or "general"
    )
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    return CATEGORY_ALIASES.get(key, key if key in CONFIG else "general")


def build_caption(post):
    category = category_for(post)
    config = CONFIG.get(category, CONFIG["general"])
    day = int(post["day"])

    hook = HOOKS[(day - 1) % len(HOOKS)]
    read_cta = READ_CTA[(day - 1) % len(READ_CTA)]
    follow_cta = FOLLOW_CTA[(day - 1) % len(FOLLOW_CTA)]

    hashtags = " ".join(config["hashtags"])

    return (
        f"{hook}\n\n"
        f"{read_cta}\n\n"
        f"If you enjoy {config['keywords']}, you’re in the right place.\n\n"
        f"{follow_cta}\n\n"
        f"{hashtags}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--output", default="outputs/caption.txt")
    args = parser.parse_args()

    post = get_post(args.day)
    caption = build_caption(post)

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(caption, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
