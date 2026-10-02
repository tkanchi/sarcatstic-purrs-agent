# SARCATSTIC PURRS Agent

Automated daily Instagram **Reel** pipeline for Milo.

## Runtime design
This version does **not** use the OpenAI API.

Pipeline:

`approved quote -> approved Milo PNG -> locked 4:5 design -> 9:16 Reel -> rights-cleared music -> category-specific caption -> Instagram Reel`

## Reel format
- Final video: **1080 x 1920 (9:16)**
- Duration: **8 seconds**
- Video: H.264, 24 fps
- Audio: AAC, 48 kHz, 128 kbps
- Gentle visual zoom for motion
- Music at 20% with short fade-in/fade-out
- Reel shared to feed

## Music — automated
Manual audio uploads are **not required**.

Like `talksnwalks-agent`, this repo contains a rights-cleared remote catalog in:

`data/rights_cleared_audio.csv`

For each campaign day the workflow:
1. matches music to the joke family: work, money, relationship, family, driving or general;
2. rotates suitable rights-cleared tracks to reduce repetition;
3. downloads the selected track during the GitHub run;
4. embeds it into the MP4;
5. saves music/license metadata beside the preview.

`assets/music/` remains available only as an optional local override/fallback.

## Approved Milo library
Approved transparent Milo cutouts live under:

`assets/milo_library/`

with category folders `work/`, `money/`, `relationship/`, `family/`, `driving/`, and `general/`.

## Captions
Every shortlisted Reel gets a category-specific caption with:
- share-first hook
- relevant discovery keywords
- save/share/follow CTA
- exactly 5 relevant hashtags
- no channel-name hashtag

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
