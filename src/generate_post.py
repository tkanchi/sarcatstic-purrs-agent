import argparse
import json
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from brand import CANVAS, FOOTER_COLOR, QUOTE_COLOR

ROOT = Path(__file__).resolve().parents[1]
CONTENT_FILE = ROOT / "content" / "month_01.json"
MILO_LIBRARY = ROOT / "assets" / "milo_library"
FONT_CACHE = ROOT / ".cache" / "PatrickHand-Regular.ttf"
FONT_URL = os.getenv(
    "PATRICK_HAND_FONT_URL",
    "https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf",
)

BACKGROUND_COLORS = {
    "warm_cream": (249, 244, 232),
    "dusty_sage": (220, 227, 213),
    "muted_blue": (218, 228, 237),
    "soft_blush": (247, 226, 220),
}

CATEGORY_ALIASES = {
    # Work family
    "work": "work",
    "it": "work",
    "it_job": "work",
    "meeting": "work",
    "meetings": "work",
    "manager": "work",
    # Money family
    "money": "money",
    "salary": "money",
    # Relationship family
    "relationship": "relationship",
    "relationships": "relationship",
    "marriage": "relationship",
    "wife": "relationship",
    "husband": "relationship",
    # Family family
    "family": "family",
    "sister": "family",
    "brother": "family",
    # Driving family
    "driving": "driving",
    "traffic": "driving",
    # General fallback family
    "general": "general",
    "everyday": "general",
    "social": "general",
    "mood": "general",
    "adulting": "general",
    "productivity": "general",
    "overthinking": "general",
}


def load_post(day):
    rows = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    return next(row for row in rows if row["day"] == day)


def ensure_font():
    override = os.getenv("PATRICK_HAND_FONT_PATH", "").strip()
    if override:
        path = Path(override)
        if not path.exists():
            raise FileNotFoundError(path)
        return path

    FONT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    if not FONT_CACHE.exists():
        urllib.request.urlretrieve(FONT_URL, FONT_CACHE)
    return FONT_CACHE


def normalize_category(value):
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return CATEGORY_ALIASES.get(key, key or "general")


def approved_milo_files(category=None):
    """Return approved PNG illustrations, optionally from one category folder."""
    if not MILO_LIBRARY.exists():
        return []

    if category:
        folder = MILO_LIBRARY / normalize_category(category)
        if not folder.exists():
            return []
        return sorted(
            path for path in folder.rglob("*.png")
            if path.is_file()
        )

    return sorted(
        path for path in MILO_LIBRARY.rglob("*.png")
        if path.is_file()
    )


def resolve_assigned_illustration(assigned):
    """Resolve either category/file.png or a unique filename anywhere in the library."""
    assigned = assigned.strip().replace("\\", "/")
    direct = MILO_LIBRARY / assigned
    if direct.exists() and direct.is_file() and direct.suffix.lower() == ".png":
        return direct

    # Allow content rows to specify just the filename.
    matches = [
        path for path in MILO_LIBRARY.rglob(Path(assigned).name)
        if path.is_file() and path.suffix.lower() == ".png"
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        choices = ", ".join(str(p.relative_to(MILO_LIBRARY)) for p in matches)
        raise RuntimeError(
            f"Illustration filename is ambiguous: {assigned}. Matches: {choices}"
        )

    raise FileNotFoundError(
        f"Assigned Milo illustration is missing: {assigned}. "
        "Upload the approved transparent PNG under assets/milo_library/."
    )


def select_milo_asset(post, day):
    # Best case: Month 1 explicitly maps the quote to the exact Milo pose.
    assigned = str(post.get("illustration", "")).strip()
    if assigned:
        return resolve_assigned_illustration(assigned)

    # Otherwise choose from the correct visual family.
    category_hint = (
        post.get("illustration_category")
        or post.get("category")
        or post.get("pillar")
        or "general"
    )
    category = normalize_category(category_hint)
    files = approved_milo_files(category)

    # If a category folder is unexpectedly empty, use general before using the whole library.
    if not files and category != "general":
        files = approved_milo_files("general")

    if not files:
        files = approved_milo_files()

    if not files:
        raise FileNotFoundError(
            "No approved Milo PNGs found under assets/milo_library/. "
            "Upload at least one transparent Milo cutout."
        )

    # Deterministic rotation: the same campaign day always selects the same fallback image.
    return files[(day - 1) % len(files)]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_font(draw, text, font_path, max_width, max_height):
    for size in range(76, 43, -2):
        font = ImageFont.truetype(str(font_path), size=size)
        lines = wrap_text(draw, text, font, max_width)
        spacing = max(8, size // 7)
        boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        height = sum(box[3] - box[1] for box in boxes) + spacing * (len(lines) - 1)
        if height <= max_height:
            return font, lines, spacing
    font = ImageFont.truetype(str(font_path), size=44)
    return font, wrap_text(draw, text, font, max_width), 8


def draw_paw(draw, x, y, scale=1.0):
    pad = int(5 * scale)
    toe = int(2.6 * scale)
    draw.ellipse((x-pad, y-pad, x+pad, y+pad), fill=FOOTER_COLOR)
    for ox, oy in [(-6, -7), (-2, -10), (3, -10), (7, -6)]:
        cx, cy = x + int(ox * scale), y + int(oy * scale)
        draw.ellipse((cx-toe, cy-toe, cx+toe, cy+toe), fill=FOOTER_COLOR)


def resize_milo(asset):
    milo = Image.open(asset).convert("RGBA")
    bbox = milo.getbbox()
    if bbox:
        milo = milo.crop(bbox)

    max_w, max_h = 760, 650
    scale = min(max_w / milo.width, max_h / milo.height, 1.0)
    size = (max(1, int(milo.width * scale)), max(1, int(milo.height * scale)))
    return milo.resize(size, Image.Resampling.LANCZOS)


def build_post(post, day, output_path):
    bg = BACKGROUND_COLORS.get(post["background"])
    if bg is None:
        raise ValueError(f"Unknown background family: {post['background']}")

    image = Image.new("RGBA", CANVAS, bg + (255,))
    draw = ImageDraw.Draw(image)
    font_path = ensure_font()

    margin = 84
    quote_font, lines, spacing = fit_font(
        draw,
        post["quote"],
        font_path,
        CANVAS[0] - (2 * margin),
        340,
    )

    y = 72
    for line in lines:
        box = draw.textbbox((0, 0), line, font=quote_font)
        width = box[2] - box[0]
        height = box[3] - box[1]
        x = margin if post["quote_position"] == "upper_left" else (CANVAS[0] - width) // 2
        draw.text((x, y), line, font=quote_font, fill=QUOTE_COLOR)
        y += height + spacing

    asset = select_milo_asset(post, day)
    milo = resize_milo(asset)

    mx = (CANVAS[0] - milo.width) // 2
    my = min(1120 - milo.height, max(460, 1180 - milo.height))

    shadow_w = int(milo.width * 0.62)
    shadow_h = 26
    shadow_x = CANVAS[0] // 2
    shadow_y = min(1160, my + milo.height - 8)
    draw.ellipse(
        (
            shadow_x - shadow_w // 2,
            shadow_y - shadow_h // 2,
            shadow_x + shadow_w // 2,
            shadow_y + shadow_h // 2,
        ),
        fill=(0, 0, 0, 22),
    )

    image.alpha_composite(milo, (mx, my))

    footer_font = ImageFont.truetype(str(font_path), size=38)
    footer_word = "SARCATSTIC"
    box = draw.textbbox((0, 0), footer_word, font=footer_font)
    footer_width = box[2] - box[0]
    total_width = footer_width + 34
    fx = (CANVAS[0] - total_width) // 2
    fy = CANVAS[1] - 78
    draw.text((fx, fy), footer_word, font=footer_font, fill=FOOTER_COLOR)
    draw_paw(draw, fx + footer_width + 19, fy + 23, scale=1.15)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)

    relative_asset = asset.relative_to(MILO_LIBRARY)
    print(f"Using Milo asset: {relative_asset}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    args = parser.parse_args()

    post = load_post(args.day)
    output_path = ROOT / "outputs" / f"day_{args.day:02d}.png"
    build_post(post, args.day, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
