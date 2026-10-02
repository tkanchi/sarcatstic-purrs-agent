import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image

from brand import BACKGROUND_COLORS

ROOT = Path(__file__).resolve().parents[1]
CONTENT_FILE = ROOT / "content" / "month_01.json"
MUSIC_LIBRARY = ROOT / "assets" / "music"
OUTPUTS = ROOT / "outputs"

REEL_SIZE = (1080, 1920)
REEL_SECONDS = 8
FPS = 24
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac"}

CATEGORY_ALIASES = {
    "it": "work",
    "it_job": "work",
    "meeting": "work",
    "meetings": "work",
    "manager": "work",
    "salary": "money",
    "marriage": "relationship",
    "wife": "relationship",
    "husband": "relationship",
    "sister": "family",
    "brother": "family",
    "traffic": "driving",
    "relationships": "relationship",
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


def category_for(post):
    raw = (
        post.get("music_category")
        or post.get("category")
        or post.get("pillar")
        or "general"
    )
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    return CATEGORY_ALIASES.get(key, key or "general")


def available_music():
    if not MUSIC_LIBRARY.exists():
        return []
    return sorted(
        p for p in MUSIC_LIBRARY.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )


def select_music(post, day):
    assigned = str(post.get("music", "")).strip()
    if assigned:
        direct = MUSIC_LIBRARY / assigned
        if direct.exists() and direct.is_file():
            return direct
        matches = [p for p in available_music() if p.name == Path(assigned).name]
        if len(matches) == 1:
            return matches[0]
        raise FileNotFoundError(f"Assigned music track not found: {assigned}")

    files = available_music()
    if not files:
        raise FileNotFoundError(
            "No music tracks found in assets/music/. "
            "Upload at least one royalty-free/original track before building Reels."
        )

    category = category_for(post)
    category_files = [
        p for p in files
        if p.stem.lower().startswith(f"music_{category}_")
    ]
    if not category_files:
        category_files = [
            p for p in files
            if p.stem.lower().startswith("music_general_")
        ]
    if not category_files:
        category_files = files

    return category_files[(day - 1) % len(category_files)]


def make_reel_frame(source_path, post, output_path):
    bg = BACKGROUND_COLORS[post["background"]]
    source = Image.open(source_path).convert("RGB")

    target_width = REEL_SIZE[0]
    target_height = round(target_width * 5 / 4)
    source = source.resize((target_width, target_height), Image.Resampling.LANCZOS)

    frame = Image.new("RGB", REEL_SIZE, bg)
    y = (REEL_SIZE[1] - target_height) // 2
    frame.paste(source, (0, y))
    frame.save(output_path, "PNG", optimize=True)


def build_reel(day):
    post = load_post(day)
    source = OUTPUTS / f"day_{day:02d}.png"
    if not source.exists():
        raise FileNotFoundError(f"Branded source image missing: {source}")

    frame = OUTPUTS / f"day_{day:02d}_reel_frame.png"
    output = OUTPUTS / f"day_{day:02d}.mp4"
    make_reel_frame(source, post, frame)

    music = select_music(post, day)

    frames = REEL_SECONDS * FPS
    vf = (
        "zoompan="
        "z='min(zoom+0.00035,1.025)':"
        "x='iw/2-(iw/zoom/2)':"
        "y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=1080x1920:fps={FPS},"
        "format=yuv420p"
    )
    af = (
        f"atrim=0:{REEL_SECONDS},"
        "afade=t=in:st=0:d=0.25,"
        f"afade=t=out:st={REEL_SECONDS - 0.75}:d=0.75,"
        "volume=0.20"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(frame),
        "-stream_loop", "-1", "-i", str(music),
        "-t", str(REEL_SECONDS),
        "-vf", vf,
        "-af", af,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-ar", "48000",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-shortest",
        str(output),
    ]
    subprocess.run(cmd, check=True)

    print(f"Music: {music.relative_to(MUSIC_LIBRARY)}")
    print(output)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    args = parser.parse_args()
    build_reel(args.day)


if __name__ == "__main__":
    main()
