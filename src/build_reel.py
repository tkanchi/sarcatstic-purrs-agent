import argparse
import csv
import json
import subprocess
from pathlib import Path

import requests
from PIL import Image

from brand import BACKGROUND_COLORS

ROOT = Path(__file__).resolve().parents[1]
CONTENT_FILE = ROOT / "content" / "month_01.json"
RIGHTS_AUDIO_FILE = ROOT / "data" / "rights_cleared_audio.csv"
MUSIC_LIBRARY = ROOT / "assets" / "music"
OUTPUTS = ROOT / "outputs"

REEL_SIZE = (1080, 1920)
REEL_SECONDS = 8
FPS = 24
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}

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

CATEGORY_MOODS = {
    "general": ("joyful", "reflective", "cinematic"),
    "work": ("bold", "energy", "cinematic"),
    "money": ("bold", "reflective", "energy"),
    "relationship": ("warm", "reflective", "joyful"),
    "family": ("joyful", "warm", "reflective"),
    "driving": ("energy", "bold", "joyful"),
}


def load_posts():
    return json.loads(CONTENT_FILE.read_text(encoding="utf-8"))


def load_post(day):
    return next(row for row in load_posts() if row["day"] == day)


def category_for(post):
    raw = (
        post.get("music_category")
        or post.get("category")
        or post.get("pillar")
        or "general"
    )
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    return CATEGORY_ALIASES.get(key, key or "general")


def _active(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def load_rights_audio():
    if not RIGHTS_AUDIO_FILE.exists():
        return []
    with RIGHTS_AUDIO_FILE.open(newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f) if _active(row.get("Active"))]


def _topics(row):
    return {
        item.strip().lower()
        for item in str(row.get("Topics") or "").split(";")
        if item.strip()
    }


def _score(row, category):
    moods = CATEGORY_MOODS.get(category, CATEGORY_MOODS["general"])
    mood = str(row.get("Mood") or "").strip().lower()
    score = 0

    if mood == moods[0]:
        score += 70
    elif len(moods) > 1 and mood == moods[1]:
        score += 45
    elif len(moods) > 2 and mood == moods[2]:
        score += 25

    if category in _topics(row):
        score += 60

    return score


def choose_rights_track(day):
    """Simulate campaign days so tracks rotate before repeating where possible."""
    rows = load_rights_audio()
    if not rows:
        return None

    posts = load_posts()
    used = set()
    chosen = None

    for index in range(day):
        if len(used) >= len(rows):
            used.clear()

        post = posts[index]
        category = category_for(post)
        available = [r for r in rows if r.get("TrackID") not in used]
        available.sort(key=lambda r: (-_score(r, category), r.get("TrackID", "")))

        shortlist = available[: min(4, len(available))]
        chosen = shortlist[index % len(shortlist)]
        used.add(chosen.get("TrackID"))

    return chosen


def download_rights_track(row, day):
    url = str(row.get("DownloadURL") or "").strip()
    if not url.startswith("https://"):
        raise ValueError(f"Invalid audio URL for {row.get('TrackID', '')}")

    suffix = Path(url.split("?", 1)[0]).suffix.lower()
    if suffix not in AUDIO_EXTENSIONS:
        suffix = ".mp3"

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    destination = OUTPUTS / f"day_{day:02d}_music_{row.get('TrackID', 'track')}{suffix}"

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    written = 0
    try:
        with destination.open("wb") as f:
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)
        if written < 4096:
            raise RuntimeError(f"Downloaded music file is unexpectedly small: {written} bytes")
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return destination


def available_local_music():
    if not MUSIC_LIBRARY.exists():
        return []
    return sorted(
        p for p in MUSIC_LIBRARY.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )


def select_music(post, day):
    # Optional exact local override, if we ever want one for a special Reel.
    assigned = str(post.get("music", "")).strip()
    if assigned:
        direct = MUSIC_LIBRARY / assigned
        if direct.exists() and direct.is_file():
            return direct, {
                "source": "local_approved",
                "track": direct.stem,
                "artist": "",
                "license_source": "approved local asset",
                "license_url": "",
            }

    # Normal production path: same rights-cleared remote approach used by talksnwalks-agent.
    row = choose_rights_track(day)
    if row:
        path = download_rights_track(row, day)
        return path, {
            "source": "rights_cleared_remote",
            "track_id": row.get("TrackID", ""),
            "track": row.get("Track", ""),
            "artist": row.get("Artist", ""),
            "mood": row.get("Mood", ""),
            "license_source": row.get("Source", ""),
            "license_url": row.get("LicenseURL", ""),
        }

    # Emergency fallback only if the remote catalog is unavailable.
    files = available_local_music()
    if files:
        path = files[(day - 1) % len(files)]
        return path, {
            "source": "local_fallback",
            "track": path.stem,
            "artist": "",
            "license_source": "approved local asset",
            "license_url": "",
        }

    raise FileNotFoundError(
        "No rights-cleared remote audio or approved local fallback is available."
    )


def make_reel_frame(source_path, post, output_path):
    source = Image.open(source_path).convert("RGB")
    if source.size != REEL_SIZE:
        source = source.resize(REEL_SIZE, Image.Resampling.LANCZOS)
    source.save(output_path, "PNG", optimize=True)


def build_reel(day):
    post = load_post(day)
    source = OUTPUTS / f"day_{day:02d}.png"
    if not source.exists():
        raise FileNotFoundError(f"Branded source image missing: {source}")

    frame = OUTPUTS / f"day_{day:02d}_reel_frame.png"
    output = OUTPUTS / f"day_{day:02d}.mp4"
    metadata_path = OUTPUTS / f"day_{day:02d}_music.json"
    make_reel_frame(source, post, frame)

    music, music_info = select_music(post, day)

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

    metadata_path.write_text(
        json.dumps(
            {
                "day": day,
                "category": category_for(post),
                **music_info,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Music: {music_info.get('artist', '')} - {music_info.get('track', '')} "
        f"({music_info.get('source', '')})"
    )
    print(output)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True)
    args = parser.parse_args()
    build_reel(args.day)


if __name__ == "__main__":
    main()
