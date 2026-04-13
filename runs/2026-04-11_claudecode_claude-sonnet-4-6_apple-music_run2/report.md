# Benchmark Report: apple-music — claudecode (Sonnet 4.6) — Run 2

**Date:** 2026-04-11
**Platform:** claudecode (claude-sonnet-4-6)
**Skill version:** f323b95
**Query:** "bohemian rhapsody queen"

## Summary

| Metric | Value |
|--------|-------|
| Wall total | 16.036s |
| Tool calls | 1.198s |
| LLM overhead | 14.838s (92.5%) |
| Output size | 964 KB M4A |
| Top result | Bohemian Rhapsody by Queen |
| Estimated cost | $0.2848 |

## Timings

| Step | Time |
|------|------|
| search_apple_music | 520ms |
| search_and_download_preview | 678ms |
| **Total tool calls** | **1,198ms** |
| **Wall total** | **16,036ms** |
| LLM overhead | 14,838ms |

## Key Findings

- **LLM overhead is 92.5%** of wall time — characteristic of sub-second skills where Claude orchestration dominates.
- **Both search (520ms) and download (678ms) are fast** — Apple CDN warm from prior runs in this session.
- Results very consistent with prior run2 attempt: search ~540ms avg, download ~640ms avg when CDN is warm.
- LLM overhead stable at ~15–19s regardless of skill speed.

## Comparison: Run 1 vs Run 2

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Skill version | b2f439d | f323b95 |
| search_apple_music | 611ms | 520ms |
| search_and_download_preview | 8,077ms | 678ms |
| Total tool calls | 8,688ms | 1,198ms |
| Wall total | 26.095s | 16.036s |
| LLM overhead | 17.407s (66.7%) | 14.838s (92.5%) |
| Output size | 964 KB | 964 KB |
| Estimated cost | null | $0.2848 |
