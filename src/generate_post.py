import argparse
import base64
import json
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from brand import BACKGROUND_LABELS, CANVAS, FOOTER_COLOR, MILO_TRAITS, QUOTE_COLOR

ROOT = Path(__file__).resolve().parents[1]
CONTENT_FILE = ROOT / "content" / "month_01.json"
COLLAGE = ROOT / "assets" / "milo_collage.jpg"
PROFILE = ROOT / "assets" / "milo_profile.jpg"
FONT_CACHE = ROOT / ".cache" / "PatrickHand-Regular.ttf"
FONT_URL = os.getenv(
    "PATRICK_HAND_FONT_URL",
    "https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf",
)
MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2.5-sunburst")
QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "medium")

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

def build_visual_prompt(post):
    background = BACKGROUND_LABELS[post["background"]]
    prop = post.get("prop", "none")
    return f"""
Create one clean minimal portrait Instagram illustration using the two supplied Milo reference images.
The FIRST image is the primary source of truth for Milo's identity and appearance.
The SECOND image is supplementary. Draw ONE Milo only. Do not reproduce the collage.

Milo must remain consistent: {MILO_TRAITS}.
Expression: {post['expression']}.
Background: {background}; matte, quiet, warm, minimal and uncluttered.
Supporting object: {prop}. Never use more than 1-2 simple supporting objects.
Composition: Milo occupies the lower half, slightly off-center, with a subtle grounding shadow.
Keep the upper 35-40 percent spacious and visually quiet for text that will be added later.
Do NOT generate text, letters, captions, logos, watermarks, speech bubbles or footer copy.
Avoid busy interiors, detailed scenery, saturated colors, dramatic lighting and poster-style layouts.
Preserve Milo's face, gray-and-white markings, amber eyes, gold right-ear hoop, yellow collar and paw-print tag.
""".strip()

def generate_art(post, output_path):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for image generation")
    if not COLLAGE.exists() or not PROFILE.exists():
        raise FileNotFoundError("Milo reference images are missing from assets/")

    from openai import OpenAI
    client = OpenAI()

    with open(COLLAGE, "rb") as primary, open(PROFILE, "rb") as secondary:
        result = client.images.edit(
            model=MODEL,
            image=[primary, secondary],
            prompt=build_visual_prompt(post),
            size="1024x1536",
            quality=QUALITY,
            output_format="png",
        )

    encoded = result.data[0].b64_json
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(encoded))

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
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

def overlay_brand(art_path, post, output_path):
    font_path = ensure_font()
    source = Image.open(art_path).convert("RGB")
    image = ImageOps.fit(source, CANVAS, method=Image.Resampling.LANCZOS, centering=(0.5, 0.56))
    draw = ImageDraw.Draw(image)

    margin = 84
    quote_font, lines, spacing = fit_font(
        draw,
        post["quote"],
        font_path,
        CANVAS[0] - (2 * margin),
        350,
    )

    y = 76
    for line in lines:
        box = draw.textbbox((0, 0), line, font=quote_font)
        width = box[2] - box[0]
        height = box[3] - box[1]
        x = margin if post["quote_position"] == "upper_left" else (CANVAS[0] - width) // 2
        draw.text((x, y), line, font=quote_font, fill=QUOTE_COLOR)
        y += height + spacing

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
    image.save(output_path, "PNG", optimize=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--reuse-art", default="")
    parser.add_argument("--art-only", action="store_true")
    args = parser.parse_args()

    post = load_post(args.day)
    out_dir = ROOT / "outputs"
    art_path = Path(args.reuse_art) if args.reuse_art else out_dir / f"day_{args.day:02d}_art.png"
    final_path = out_dir / f"day_{args.day:02d}.png"

    if not args.reuse_art:
        generate_art(post, art_path)

    if args.art_only:
        print(art_path)
        return

    overlay_brand(art_path, post, final_path)
    print(final_path)

if __name__ == "__main__":
    main()
