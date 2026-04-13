# Benchmark Report: apple-music-reference on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** Search Apple Music for "bohemian rhapsody queen" and download 30s preview
**Session:** sesn_011CZui4SAgVNhAWgmaTP8t6

## Results

| Metric | Value |
|--------|-------|
| Wall total | **146.5s** |
| Tool execution | 28.6s (20%) |
| LLM overhead | 117.9s (80%) |
| Tokens (total) | 170,244 |
| Estimated cost | $0.200 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Read SKILL.md | 10.7s | 2.9s | 13.6s |
| Search (with DNS debug) | 11.0s | 86.0s | 97.0s |
| Search + download preview | 1.4s | — | 1.4s |
| CDN upload | 2.4s | 14.9s | 17.3s |

## Observations

- **LLM overhead dominated at 80%** — the highest of all 4 skills benchmarked. Actual skill execution was only ~4.8s (search 1.15s + download 1.94s + upload 1.7s).
- **DNS resolution error on first attempt** — the agent's initial search call failed with `[Errno -3] Temporary failure in name resolution`. The agent spent significant time debugging: reading the script source, testing curl connectivity, retrying with different approaches.
- **12 LLM calls, 5622 output tokens** — 3x more output tokens than other skills due to all the debugging reasoning.
- **170K total tokens** — highest token usage across all benchmarks, driven by cache reads (145K) from the many LLM calls accumulating context.
- **Cost: $0.200** — most expensive run, 3x more than video-captions ($0.064). The DNS debugging loop burned tokens.
- **Actual skill is blazing fast** — once DNS resolved, search=1.15s, download=1.94s, upload=1.7s. Total ~4.8s of real work.
- **Track found:** Bohemian Rhapsody by Queen, 962KB M4A preview, 30 seconds.

## Output

CDN URL: https://msaocnoosm1a4.pika.art/v2/files/agent/f1abaf3a-68c6-492e-abf1-3b6febd8a6e1/preview.m4a
