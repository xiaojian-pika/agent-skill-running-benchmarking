# Benchmark Report: video-captions — claudecode (Sonnet 4.6) — Run 2

**Date:** 2026-04-11
**Platform:** claudecode (claude-sonnet-4-6)
**Skill version:** f323b95
**Test input:** charli-daily-vlog.mp4 (67.8s, 4.9MB, HEVC+AAC)

## Summary

| Metric | Value |
|--------|-------|
| Wall total | 28.039s |
| Tool calls | 11.194s |
| LLM overhead | 16.845s (60.1%) |
| Output size | 30,712 KB |
| Transcription | Whisper API (132 words) |
| Estimated cost | $0.3166 |

## Timings

| Step | Time |
|------|------|
| Download video | 314ms |
| Probe video | 9ms |
| caption_script_full (API path) | 10,871ms |
| **Total tool calls** | **11,194ms** |
| **Wall total** | **28,039ms** |
| LLM overhead | 16,845ms |

## Key Findings

- **API transcription (Whisper) is much faster than local CPU.** Run 1 used local faster-whisper (small, CPU int8) with 32s total caption script. This run used Whisper API and took 10.9s — a 2.9× speedup.
- **LLM overhead is 60.1%** of wall time — high because the skill itself is fast, making between-step Claude thinking proportionally large.
- Whisper API succeeded on first try (132 words). Staging key ak_zBO3WUAGn... valid.
- Output: 30,712 KB (run1: 30,720 KB) — virtually identical.

## Comparison: Run 1 vs Run 2

| Metric | Run 1 (local faster-whisper) | Run 2 (Whisper API) |
|--------|------------------------------|---------------------|
| Skill version | b2f439d | f323b95 |
| caption_script_full | 32.048s | 10.871s |
| Wall total | 76.958s | 28.039s |
| LLM overhead | 23.081s (30%) | 16.845s (60.1%) |
| Output size | 30,720 KB | 30,712 KB |
| Transcription method | faster-whisper small CPU int8 | Whisper API (proxy) |
| Estimated cost | null | $0.3166 |
