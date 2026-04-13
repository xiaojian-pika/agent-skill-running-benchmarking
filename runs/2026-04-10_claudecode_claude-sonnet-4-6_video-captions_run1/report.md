# Benchmark Report: video-captions — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** Add TikTok-style captions to charli-daily-vlog.mp4 (720x1280, 67.8s, 4.9MB)

## Timing Summary

| Step | Time |
|------|------|
| Download video (S3 → devbox) | 0.091s |
| ffprobe | 0.010s |
| Extract audio (standalone) | 0.394s |
| Transcribe faster-whisper (standalone) | 21.334s |
| Full caption script (tiktok) | 32.048s |
| **Total tool calls** | **53.877s** |
| **LLM overhead** | **23.081s** |
| **Wall total** | **76.958s** |

- LLM overhead: 30.0% of wall time
- Skill/tool execution: 70.0% of wall time

## Observations

- **Transcription:** 21.3s for 67.8s audio (faster-whisper small CPU int8). CPU load variability on shared devbox.
- **Caption script:** 32.0s total including audio extraction, transcription, ass generation, and ffmpeg burn.
- **Download fast:** 91ms — S3/CDN cache likely warm.
- **ffprobe near-instant:** 10ms.
- **LLM overhead consistent:** ~23s in both this run and the opus run, suggesting it's bounded by prompt/context processing time, not model speed.
- **Token cost lower than opus:** $1.47 vs $4.02 despite more output tokens (28.6K vs 7.2K), due to Sonnet's lower per-token pricing.
- **Output correct:** 138 words detected, 30720 KB output.
