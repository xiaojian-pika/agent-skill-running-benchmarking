# Benchmark Report: music-beat-sync — claudecode (Sonnet 4.6) — Run 2

**Date:** 2026-04-11
**Platform:** claudecode (claude-sonnet-4-6)
**Skill version:** f323b95
**Test input:** charli-daily-vlog.mp4 (67.8s, 4.9MB, HEVC+AAC)

## Summary

| Metric | Value |
|--------|-------|
| Wall total | 185.864s |
| Tool calls | 163.050s |
| LLM overhead | 22.814s (12.3%) |
| Output size | 16,440 KB |
| Music generated | 15.9s track @ 120 BPM |
| Estimated cost | $0.4807 |

## Timings

| Step | Time |
|------|------|
| Download video | 178ms |
| Probe video | 8ms |
| scene_detection (26 cuts) | 2,343ms |
| music_generation_minimax | 123,400ms |
| beat_alignment_encode (est.) | 37,121ms |
| beat_sync_full (total) | 160,521ms |
| **Total tool calls** | **163,050ms** |
| **Wall total** | **185,864ms** |
| LLM overhead | 22,814ms |

## Key Findings

- **Music generation (123.4s) is longer than run1 (81.7s)** — MiniMax API latency is highly variable. Across all runs: 77.9s, 81.7s, 121.9s, 123.4s.
- **Generated track: 15.9s** — shortest across all runs (run1: 18.3s, prior attempts: 33.9s, 14.4s). Track length non-deterministic.
- **LLM overhead 12.3%** — consistent with run1's 18.0%. Skill's MiniMax wait dominates, keeping LLM overhead proportion low.
- **26 scene cuts** detected (identical across all runs — deterministic).
- Clean run — no timeouts or retries.

## Comparison: Run 1 vs Run 2

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Skill version | b2f439d | f323b95 |
| Music generation | 81.7s (18.3s track) | 123.4s (15.9s track) |
| beat_sync_full | 121.115s | 160.521s |
| Wall total | 150.987s | 185.864s |
| LLM overhead | 27.215s (18.0%) | 22.814s (12.3%) |
| Output size | 16,444 KB | 16,440 KB |
| Estimated cost | null | $0.4807 |
