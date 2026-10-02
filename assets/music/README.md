# SARCATSTIC PURRS Music

No manual music upload is required for normal production.

The Reel builder reuses the same rights-cleared remote-audio pattern as the user's `talksnwalks-agent`:

1. read `data/rights_cleared_audio.csv`
2. choose a suitable track for the day's joke category
3. rotate tracks to reduce repetition
4. download the selected rights-cleared track during the GitHub Actions run
5. embed it into the 8-second MP4 with FFmpeg
6. record track/source/license metadata in `outputs/day_XX_music.json`

`assets/music/` is now optional and exists only for a future approved local override/fallback.

Do not place copyrighted commercial tracks here unless the required rights have been secured.
