# Short Ads Benchmark — Run 1 Prompt

**Platform:** pikabot  
**Model:** claude-sonnet-4-6  
**Thinking level:** medium  
**Date:** 2026-04-23  
**Test case:** TC-01 — Apple sandwich product ad, 16:9, 30s

## Prompt sent to agent

Make a 30-second product ad for "Crispello" — a premium artisan apple-and-honey sandwich brand. 

Product reference: floating apple + toast setup (vivid blue studio background, clean minimal style).
Character reference: same floating apple-toast composition as brand visual identity.

Creative direction: playful food magic, telekinetic assembly, golden warm tones with blue studio backdrop. Tagline: "Made with wonder."

Voice: Brian (deep resonant English).

Reference images:
- Image 1: /data/.pikabot/workspace/media/inbound/af5eb3256d5f5f8b.jpg (product first frame — floating apple + toast)
- Image 2: /data/.pikabot/workspace/media/inbound/59ac9f39cff13cf3.jpg (product explosion frame — deconstructed sandwich)

## Expected output
- 30s final.mp4 (2×15s acts, 16:9, 720p)
- BGM: warm cinematic instrumental ≥30s
- VO: slogan "Made with wonder." via Brian voice
- Border fix applied, CRF 16 encode
- CDN or local file URL
