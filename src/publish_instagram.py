import json
import os
import sys
import time
from pathlib import Path

import requests

GRAPH_HOST = os.getenv("META_GRAPH_HOST", "https://graph.instagram.com").rstrip("/")
API_VERSION = os.getenv("META_API_VERSION", "v26.0")
IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "").strip()
VIDEO_URL = os.getenv("VIDEO_URL", "").strip()
CAPTION_FILE = Path(os.getenv("CAPTION_FILE", "outputs/caption.txt"))
RESULT_FILE = Path(os.getenv("RESULT_FILE", "published_logs/publish_result.json"))


def require(name, value):
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")


def request_json(method, url, **kwargs):
    response = requests.request(method, url, timeout=90, **kwargs)
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}
    if not response.ok:
        raise RuntimeError(f"Instagram API error {response.status_code}: {payload}")
    return payload


def create_container(caption):
    payload = request_json(
        "POST",
        f"{GRAPH_HOST}/{API_VERSION}/{IG_USER_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": VIDEO_URL,
            "caption": caption,
            "share_to_feed": "true",
            "audio_name": "SARCATSTIC PURRS",
            "access_token": ACCESS_TOKEN,
        },
    )
    container_id = payload.get("id")
    if not container_id:
        raise RuntimeError(f"Instagram did not return a container id: {payload}")
    return container_id


def wait_until_ready(container_id, timeout_seconds=600):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        payload = request_json(
            "GET",
            f"{GRAPH_HOST}/{API_VERSION}/{container_id}",
            params={"fields": "status_code,status", "access_token": ACCESS_TOKEN},
        )
        status = payload.get("status_code", "")
        print(f"Container status: {status}")
        if status in {"FINISHED", "PUBLISHED"}:
            return
        if status in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container failed: {payload}")
        time.sleep(8)
    raise TimeoutError("Instagram Reel container was not ready in time")


def publish(container_id):
    payload = request_json(
        "POST",
        f"{GRAPH_HOST}/{API_VERSION}/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": ACCESS_TOKEN},
    )
    media_id = payload.get("id")
    if not media_id:
        raise RuntimeError(f"Instagram did not return a media id: {payload}")
    return media_id


def main():
    require("IG_USER_ID", IG_USER_ID)
    require("META_ACCESS_TOKEN", ACCESS_TOKEN)
    require("VIDEO_URL", VIDEO_URL)

    caption = CAPTION_FILE.read_text(encoding="utf-8").strip()
    container_id = create_container(caption)
    wait_until_ready(container_id)
    media_id = publish(container_id)

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULT_FILE.write_text(
        json.dumps(
            {
                "status": "PUBLISHED",
                "media_type": "REELS",
                "container_id": container_id,
                "media_id": media_id,
                "video_url": VIDEO_URL,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Published Instagram Reel media id: {media_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
