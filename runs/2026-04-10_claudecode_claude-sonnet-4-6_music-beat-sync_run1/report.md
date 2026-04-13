# Benchmark Report: music-beat-sync — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** Add hype beat-synced music to charli-daily-vlog.mp4 (720x1280, 67.8s, 4.9MB)
**Result:** SUCCESS — 16.1 MB output

## Timing Summary

| Step | Time |
|------|------|
| Download video (S3 → devbox) | 0.136s |
| ffprobe | 0.009s |
| Scene detection (26 cuts) | 2.512s |
| music_generation_minimax | 81.7s |
| beat_alignment_encode + audio_mix | ~39.4s |
| beat_sync_full (total script) | 121.115s |
| **Total tool calls** | **123.772s** |
| **LLM overhead** | **27.215s** |
| **Wall total** | **150.987s** |

- LLM overhead: 18.0% of wall time
- Skill/tool execution: 82.0% of wall time

## Observations

- **MiniMax dominates:** Music generation took 81.7s (54% of wall total) — the single biggest bottleneck. Generated a short 18.3s track (typical short-track case); skill looped it automatically to fill 67.8s.
- **Beat alignment + encode fast:** ~39.4s for 26-cut speed-adjustment + ffmpeg re-encode of a 67.8s video.
- **Scene detection is negligible:** 2.5s standalone, also run internally within beat_sync_full.
- **LLM overhead lowest of all claudecode runs:** 18% / 27s — consistent with other runs (~23-34s), percentage low because total wall time is long.
- **Short-track issue confirmed:** MiniMax generated 18.3s for a 67.8s video (notes say 15-31s is common). Looping works but may sound repetitive.
- **Output size:** 16.4 MB — reasonable for 67.8s at default quality.
