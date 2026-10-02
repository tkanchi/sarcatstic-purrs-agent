# SARCATSTIC PURRS Agent

Automated daily image-post pipeline for the Milo sarcasm channel.

## Runtime design
This version does **not** use the OpenAI API.

The automation assembles each post from approved assets:

`approved quote -> approved transparent Milo PNG -> locked background -> Patrick Hand quote -> exact footer -> caption -> Instagram publish`

No `OPENAI_API_KEY` is required.

## Month 1
- Target publish time: **5:00 PM Asia/Kolkata**
- Canvas: **4:5**
- Format: **one short relatable quote + Milo + exact footer**

## Approved Milo library
Put approved transparent Milo cutouts in:

`assets/milo_library/`

PNG is preferred. The build script:
1. uses a specific `illustration` filename from the content row when one is assigned;
2. otherwise rotates deterministically through the approved Milo PNGs already in the library.

This keeps Milo consistent and avoids generating a new character every day.

## Required GitHub secrets for publishing
Only the Instagram/Meta publishing credentials are required:

- `IG_USER_ID`
- `META_ACCESS_TOKEN`

They are **not needed for a preview build**.

## Safety switch
Scheduled publishing stays disabled until this repository variable is explicitly set:

- `AUTO_PUBLISH_ENABLED=true`

Until then, manually run the workflow with `publish=false` to preview safely.

## Schedule
The workflow starts at **11:15 UTC / 4:45 PM IST** and waits until **5:00 PM IST** before publishing. GitHub scheduled workflows can start late, so 5 PM is the target rather than a hard real-time guarantee.

## Manual preview
Open:

**Actions -> Daily SARCATSTIC PURRS Post -> Run workflow**

Choose a campaign day and leave **publish** unchecked.

## Locked brand rules
See `BRAND_CONTRACT.md`.

The runtime keeps:
- Patrick Hand Regular
- black regular quote text
- exact footer treatment
- four locked background families
- 4:5 composition
- approved Milo assets only

## Important
The repository must remain public for the current Meta publishing method because Instagram needs a public URL to fetch the final image.
