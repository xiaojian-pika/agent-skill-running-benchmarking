# Benchmark Report: short-film — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-15
**Platform:** Claude Code (local Mac)
**Model:** Claude Sonnet 4.6
**Task:** Generate ~60s horror short film from 7-question creative brief (portrait 9:16)
**Result:** SUCCESS — 40.3MB, 59s output, CDN delivered
**Project ID:** film_20260415_335e2f

> **Note:** This is an abbreviated run. Stages 2+3 (asset/keyframe Gemini generation) were skipped — images reused from a prior project. Stage 4.5 had no fal lipsync — dialogue moved to sfx_hint. See "Deviations" below.

## Timing Summary

| Step | Duration |
|------|----------|
| Stage 0: init (project dir + project.json) | ~30s |
| Stage 1: plan (Claude writes story JSON) | ~60s |
| Stage 2: assets (SKIPPED — file copy) | ~5s |
| Stage 3: keyframes (SKIPPED — file copy) | ~10s |
| Stage 3.5: music (MiniMax music-2.5) | ~182s (3m02s) |
| Stage 4: video (Kling v3 omni, 5 batches) | ~762s (12m42s) |
| └─ kling_submit (5 concurrent batches) | ~30s |
| └─ kling_poll_all_batches | 342s (5m42s) |
| └─ kling_download_assemble (ffmpeg concat) | ~51s |
| Stage 4.5: music mix (ffmpeg, no lipsync) | ~39s |
| CDN upload (40.3MB final.mp4) | ~30s |
| **Total tool calls** | **~1088s** |
| **LLM overhead** | **~176s** |
| **Wall total** | **1264s (21m04s)** |

- LLM overhead: 13.9% of wall time
- Skill/tool execution: 86.1% of wall time

## Token Usage

| Metric | Value |
|--------|-------|
| input_tokens | 63 |
| output_tokens | 25,553 |
| cache_read_tokens | 4,033,577 |
| cache_write_tokens | 473,177 |
| effective_input_tokens | 4,506,817 |
| total_tokens | 4,532,370 |
| **Estimated cost** | **$3.37** |

Extracted from session a41e3ea0 with 29 messages in the benchmark window (1150 filtered out from rest of session).

## API Bottlenecks

| API | Duration | % of wall |
|-----|----------|-----------|
| Kling v3 omni (5 batches, parallel) | 342s render | 27.1% |
| Video.py total (submit+poll+assemble) | 762s | 60.3% |
| MiniMax music-2.5 | 182s | 14.4% |
| CDN upload | ~30s | 2.4% |
| ffmpeg concat + mix | ~90s | 7.1% |

## Observations

- **Kling is the dominant bottleneck**: 5 batches ran in parallel (2-3 shots each), all completing at nearly the same time (01:14:21–01:14:25). Render time 5:42 for up to 15s of video per batch is reasonable. Serializing would take ~28 min instead of 5:42.
- **video.py startup overhead**: From subagent spawn (~01:02) to Kling batch submission (01:08:39) was ~6–7 min. This is primarily Python script startup, project.json parsing, keyframe CDN upload, and prompt construction — NOT LLM thinking. Worth optimizing.
- **MiniMax music is fast**: 3 min for a 76s horror underscore. Faster than Kling per unit of output.
- **LLM overhead low at 13.9%**: Most time is spent waiting on external APIs. Consistent with other API-heavy claudecode benchmarks.
- **Cost is dominated by cache operations**: 87.7% of cost comes from cache_write ($1.77) + cache_read ($1.21). Actual input/output tokens are minimal ($0.38). This reflects the large SKILL.md being cached and re-read across subagent spawns.
- **No lipsync in this run**: A standard run with 2 dialogue shots going through fal-ai/sync-lipsync/v2 would add approximately 4–10 min and ~$0.10–0.30 in additional API cost (fal charges per video second).

## Deviations from Standard Run

| Stage | Standard | This Run | Impact |
|-------|----------|----------|--------|
| Stage 2: assets | Gemini generates char portraits + scene images (~2–3 min) | File copy from prior project (~5s) | **-150s** |
| Stage 3: keyframes | 12× Gemini calls + PIL grid compose (~5–10 min) | File copy from prior project (~10s) | **-350s** |
| Stage 4.5: lipsync | TTS per dialogue shot + fal sync-lipsync/v2 (~5–15 min/shot) | Music mix only (ffmpeg, 39s) | **-600s** est. |

**Estimated full standard run time: ~38–54 min** (adds ~17–33 min for full asset gen + lipsync for 2 dialogue shots)

## Output

- **CDN URL:** https://cdn.pika.art/v2/files/agent/4c6d00c3-22a1-4148-87f3-b474eae057f0/final.mp4
- **Duration:** 59s
- **Resolution:** 1080×1920 (portrait 9:16)
- **File size:** 40.3MB
- **Audio:** Kling-native ambient SFX + character voices (sfx_hint) + horror underscore (MiniMax, 0.06 vol)
