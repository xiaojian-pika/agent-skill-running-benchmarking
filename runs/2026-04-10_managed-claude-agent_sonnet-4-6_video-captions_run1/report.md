# Benchmark Report: video-captions on Managed Claude Agent (Warm)

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** Add tiktok-style captions to charli-daily-vlog.mp4 (67.8s, 720x1280)
**Session:** sesn_011CZugVTAvjcBmwUsRWMhQd

## Results

| Metric | Value |
|--------|-------|
| Wall total | **71.1s** |
| Tool execution | 31.8s (45%) |
| LLM overhead | 39.3s (55%) |
| Tokens (total) | 63,239 |
| Estimated cost | $0.064 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Read SKILL.md | 3.6s | 3.5s | 7.1s |
| Download video | 3.1s | 6.2s | 9.3s |
| Caption nohup+poll | 21.5s | 2.9s | 24.4s |
| CDN upload | 3.6s | 16.0s | 19.6s |

## Observations

- **Warm run with improved prompt.** Whisper model pre-cached in environment. No pre-install time counted — fair comparison with Claude Code (which also has whisper pre-installed).
- **LLM overhead is 55%** — higher than tool execution time. This is the true overhead when tool calls are fast (no model download delays).
- **Caption script completed in 23.2s** — full pipeline (extract audio + whisper transcribe + ASS generation + ffmpeg burn) for 67.8s video.
- **nohup pattern worked perfectly** — agent followed instructions to use background + poll. No 295s timeout issues.
- **ffmpeg stderr redirected** — no context bloat from verbose ffmpeg build config. This saved ~50+ lines of wasted input tokens.
- **6 LLM calls, 1652 output tokens** — efficient. Cache read (55.5K) dominates input.
- **Cost: $0.064** — very cheap per run.

## Output

CDN URL: https://msaocnoosm1a4.pika.art/v2/files/agent/02ef492c-c3e1-463e-b129-f62e85db5bbc/captioned.mp4
