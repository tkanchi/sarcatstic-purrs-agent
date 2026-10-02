# SARCATSTIC PURRS Agent

Automated daily Instagram **Reel** pipeline for Milo.

## Runtime design
This version does **not** use the OpenAI API.

Pipeline:

`approved quote -> approved Milo PNG -> locked 4:5 design -> 9:16 Reel -> embedded music -> caption -> Instagram Reel`

No `OPENAI_API_KEY` is required.

## Reel format
- Final video: **1080 x 1920 (9:16)**
- Duration: **8 seconds**
- Video: H.264, 24 fps
- Audio: AAC, 48 kHz, 128 kbps
- Gentle visual zoom for motion
- Music mixed at 20% with short fade-in/fade-out
- Share Reel to feed: yes

The branded 4:5 design is preserved inside the 9:16 Reel so the typography and Milo layout stay consistent.

## Music library
Put approved music in:

`assets/music/`

Recommended names:
- `music_general_01.mp3`
- `music_work_01.mp3`
- `music_money_01.mp3`
- `music_relationship_01.mp3`
- `music_family_01.mp3`
- `music_driving_01.mp3`

Use only audio you are legally permitted to use.

## Approved Milo library
Approved transparent Milo cutouts live under:

`assets/milo_library/`

with category folders such as `work/`, `money/`, `relationship/`, `family/`, `driving/`, and `general/`.

## Required GitHub secrets
- `IG_USER_ID`
- `META_ACCESS_TOKEN`

## Safety switch
Scheduled publishing remains disabled until:

`AUTO_PUBLISH_ENABLED=true`

Until then, run the workflow manually with `publish=false`.

## Schedule
Target publish time: **5:00 PM Asia/Kolkata**.

## Brand
See `BRAND_CONTRACT.md` for the locked palette, Patrick Hand typography, Milo rules and footer.
