# Benchmark Report: viral-trend-finder — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** T1 find fitness (TikTok+Instagram), T2 find cooking (X), T3 analyze T1 top URL, T4 trending (general)
**Cost:** $0.4263 (input $3/M + output $15/M + cache_read $0.3/M + cache_write $3.75/M)
**Result:** SUCCESS — all 4 tasks completed

## Timing Summary

| Step | Duration | Notes |
|------|----------|-------|
| T1 — find fitness (TikTok+Instagram) | **23.9s** | 18 results |
| T2 — find cooking (X) | **3.9s** | 5 results |
| T3 — analyze full pipeline | **249.8s** | 60 frames, 20 analyzed, 10 shots |
| T4 — trending (general) | **81.3s** | 10 results |
| **Total tool calls** | **358.9s** | |
| **CC LLM overhead** | **0.154s** | single bash call, measurement noise |
| **Wall total** | **359.028s** | |

- CC LLM overhead: **~0%** (single bash call, no inter-run CC activity)
- Skill execution: **~100%** of wall time
- T3 pipeline breakdown: metadata 1.1s / download 2.2s / frame_extract 5.5s / gemini_vision 23.0s / llm_synthesis 217.8s

## Results per Test Case

### T1 — find fitness (TikTok + Instagram)
- **Results:** 18 trending videos | **Top:** @fitness.953 8.0M views (TikTok) | T3 URL selected: `@fitness.953/video/7575863220104170783`

### T2 — find cooking (X/Twitter)
- **Results:** 5 trending posts | **Top:** @ThoughtCrimes80 4.4M views, @DudespostingWs 2.6M views

### T3 — analyze @fitness.953 fitness video
- **Video:** 60s, 12180KB — 60 frames extracted at 1fps, 20 sampled (max cap), 5 concurrent Gemini calls
- **Gemini Vision:** 23.0s for 20 frames (1/20 failed, synthesis proceeded)
- **LLM synthesis:** 217.8s — 2x Anthropic ReadTimeout → fell back to OpenAI; succeeded
- **Output:** 10-shot storyboard, title "Grit and Glory: Fitness Challenge", platform=tiktok

### T4 — trending (general, no niche)
- **Results:** 10 trending videos | **Top:** 73.8M views (TikTok) | TikTok native trending returned 0 → 15-query keyword fallback

## Observations

- **T3 LLM synthesis spike (217.8s):** Anthropic proxy ReadTimeout fired twice before OpenAI fallback. This single stage is 60.7% of total wall time. Gemini Vision (23.0s for 20 frames) is fast by comparison — the bottleneck is the synthesis LLM call, not the frame analysis.

- **Gemini Vision fast with 5 workers (23.0s / 20 frames = 1.15s per frame effective throughput):** The concurrency cap of 5 workers works well. Compare to prior run with 18 frames where Gemini took ~175s estimated — that estimate was wrong; actual is ~1s/frame effective with parallelism.

- **T3 video was 60s (12180KB) vs pikabot benchmark 15s (1010KB):** Larger video hit the 20-frame cap (60 frames extracted, 20 sampled). Pikabot's 15s video yielded 15 frames (no cap hit). Both completed successfully.

- **TikTok native trending consistently returns 0:** T4 always triggers the 15-query keyword fallback on this devbox. Likely a geo/API restriction. The fallback path is reliable but adds ~80s per trending call.

- **CC overhead ~0 (0.154s):** Running T1–T4 in a single bash call confirms skill execution is ~100% of wall time, consistent with SAA benchmark (0.014s overhead). The 47.8s overhead in the prior attempt was CC inter-call time, not model overhead.

- **Anthropic proxy instability:** 3 of 3 T3 runs (this run + 2 prior attempts) hit ReadTimeout on LLM synthesis. OpenAI fallback is reliable. Consistent with SAA T2 proxy spike.
