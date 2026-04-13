# Benchmark Report: music-beat-sync on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** Add hype beat-synced music to charli-daily-vlog.mp4 (67.8s, 720x1280)
**Session:** sesn_011CZuhfwKz1nogpKdQuuEHK

## Results

| Metric | Value |
|--------|-------|
| Wall total | **180.3s** |
| Tool execution | 144.1s (80%) |
| LLM overhead | 36.2s (20%) |
| Tokens (total) | 59,768 |
| Estimated cost | $0.070 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Read SKILL.md | 16.2s | 3.4s | 19.6s |
| Download video | 2.8s | 4.9s | 7.7s |
| Beat-sync nohup+poll | 121.6s | 13.9s | 135.5s |
| CDN upload | 3.6s | 14.0s | 17.6s |

## Observations

- **MiniMax music generation dominated** — beat_sync.py completed in 118.6s, with MiniMax API call being the bottleneck (60-175s typical).
- **LLM overhead is only 20%** — lowest of all skills tested, because tool execution time is so long (MiniMax).
- **nohup pattern essential** — 118.6s script would have timed out the 295s bash limit if it included retries. Using nohup+poll avoided the issue.
- **Output is 16.5MB** — larger than input (4.9MB) due to the added music track.
- **6 LLM calls, 1705 output tokens** — efficient execution.
- **Cost: $0.070** — cheap.

## Output

CDN URL: https://msaocnoosm1a4.pika.art/v2/files/agent/a5f1ce3f-16d5-41ba-a17b-a843ab197835/beat_sync_output.mp4
