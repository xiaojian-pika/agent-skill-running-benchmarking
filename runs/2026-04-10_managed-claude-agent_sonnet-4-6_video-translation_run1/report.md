# Benchmark Report: video-translation on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** Translate charli-daily-vlog.mp4 (67.8s, 720x1280) to Spanish, no lip sync
**Session:** sesn_011CZuhPKDPsJkag8N7HD1HZ

## Results

| Metric | Value |
|--------|-------|
| Wall total | **98.4s** |
| Tool execution | 68.1s (69%) |
| LLM overhead | 30.4s (31%) |
| Tokens (total) | 50,384 |
| Estimated cost | $0.060 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Read SKILL.md | 11.1s | 2.8s | 13.9s |
| Download video | 3.1s | 5.4s | 8.5s |
| Translation nohup+poll | 51.4s | 12.8s | 64.2s |
| CDN upload | 2.5s | 9.3s | 11.8s |

## Observations

- **Translation pipeline completed in 54.4s** — full API-bound pipeline: extract audio → Whisper transcribe → GPT-4o translate → ElevenLabs voice clone + TTS → ffmpeg audio replace.
- **LLM overhead is 31%** — lower than video-captions (55%) because the translation script takes longer (54s vs 23s), so tool time dominates.
- **nohup pattern worked** — no 295s timeout issues. Agent polled every 10s.
- **Output is 4.3MB** — smaller than input (4.9MB) due to TTS audio bitrate.
- **6 LLM calls, 1655 output tokens** — efficient. SKILL.md read returned an error but agent had enough context to proceed.
- **Cost: $0.060** — very cheap.

## Output

CDN URL: https://msaocnoosm1a4.pika.art/v2/files/agent/4041ddf5-1334-4bd9-98dc-7ee5d65d0d0f/translated.mp4
