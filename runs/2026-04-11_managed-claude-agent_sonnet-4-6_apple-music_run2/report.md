# Benchmark Report: apple-music-reference on Managed Claude Agent (Run 2)

**Date:** 2026-04-11
**Platform:** managed-claude-agent / Claude Sonnet 4.6
**Task:** Search Apple Music for "bohemian rhapsody queen" + download preview

## Results

| Metric | Value |
|--------|-------|
| Wall total | **138.6s** |
| Tool execution | 35.1s (25%) |
| LLM overhead | 103.5s (75%) |
| Actual skill work | ~4.6s |
| Tokens | 254,840 |
| Cost | $0.203 |

## Observations

- DNS resolution error persists on managed agent containers. Agent debugs and monkey-patches httpx each run.
- Actual skill execution ~4.6s (search 2.5s + upload 2.1s). Everything else is LLM debugging overhead.

## Output

CDN URL: https://msaocnoosm1a4.pika.art/v2/files/agent/51bf0531-4187-446b-9f9a-40a7902f2c32/preview.m4a
