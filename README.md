# SARCATSTIC PURRS Agent

Automated daily image-post pipeline for the Milo sarcasm channel.

## Month 1
- Campaign dates: **2026-10-03 through 2026-11-01**
- 30 shortlisted daily quote slots
- Target publish time: **5:00 PM Asia/Kolkata**
- Canvas: **4:5**
- Format: **one short relatable quote + Milo + exact footer**

## Pipeline
`month_01.json -> brand gate -> Milo reference-image generation -> deterministic Patrick Hand text/footer overlay -> caption -> public GitHub image URL -> Instagram publish -> log`

The AI illustration layer contains **no text**. Quote typography and the footer are added afterward with Pillow so the brand treatment stays deterministic.

## Required GitHub secrets
- `OPENAI_API_KEY`
- `IG_USER_ID`
- `META_ACCESS_TOKEN`

## Safety switch
Scheduled publishing is disabled until the repository variable below is explicitly set:

- `AUTO_PUBLISH_ENABLED=true`

Until then, use the manual workflow with `publish=false` to preview posts safely.

## Schedule
The workflow starts at **11:15 UTC / 4:45 PM IST** and waits until **5:00 PM IST** before publishing. GitHub scheduled workflows may start late, so 5 PM is the target rather than a hard real-time guarantee.

## Manual preview
Open **Actions -> Daily SARCATSTIC PURRS Post -> Run workflow**, choose a campaign day 1-30 and leave `publish` unchecked.

## Brand files
- `BRAND_CONTRACT.md`
- `assets/milo_collage.jpg` — primary source of truth
- `assets/milo_profile.jpg` — supplementary reference
- `content/month_01.json`

## Important
The repository must remain public for the current Meta publishing method because Instagram needs a public URL from which to fetch the final image.
