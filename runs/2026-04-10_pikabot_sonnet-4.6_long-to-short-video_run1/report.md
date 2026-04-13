# long-to-short-video Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** long-to-short-video v1.0.5
**Video:** Matt Cutts "Try Something New for 30 Days" (3m27s, H264, 8MB)

## Results

| Metric | Value |
|--------|-------|
| Wall total | **1923.6s** (~32 min incl. T1 kill/rerun overhead) |
| Tool calls | 1510s (78.5%) |
| LLM overhead | 413.6s (21.5%) |
| Total tokens | 3,845,391 |
| Estimated cost | $2.8926 |

## Timing breakdown

| Step | Time | Apify | Whisper | LLM | Clips |
|------|------|-------|---------|-----|-------|
| T1 fresh 3-clip tiktok | ~442s (est.) | 42s | 6s | 9s | 3 clips |
| T2 cache hit | **0.184s** | skip | skip | skip | 3 clips (checkpoint) |
| T3 fresh 3-clip hormozi | 442.7s | 36s | 7s | 10s | 3 clips |
| T4 fresh 5-clip tiktok | 441.5s | 52s | 8s | 12s | 3/5 clips |
| T1b re-run (clip 3 only) | 123.4s | skip | skip | skip | 1 clip |

## Per-clip breakdown (avg across T3/T4)

| Stage | Time |
|-------|------|
| S1 Apify | 36–52s |
| S1 download | ~0s (instant, 8MB) |
| S1 face timeline | ~20s (H264 fast decode) |
| S2 Whisper transcription | 6–8s |
| S3 LLM clip selection | 9–12s |
| S4–S6 per clip (extract+reframe+captions) | ~115–125s avg |
| S7 CDN upload per clip | ~5s |

## Key observations

- **T2 cache hit: 0.184s** — lightning fast. All 4 layers cached (video + face timeline + transcript + clip selection + done.json checkpoints).
- **Per-clip S4-S7 is the bottleneck**: ~119s avg per clip. OpenCV face detection + keyframe-based reframe accounts for most of this.
- **T4 clips_returned=3 (requested 5)**: 3m27s video only has 3 viable ~45s segments. LLM correctly identified this.
- **Face timeline H264 ~20s** (not ~60s): H264 soft-decode is faster than AV1. mmco warnings are benign.
- **T1 original killed at ~510s** during clip 3 CDN upload (process SIGTERM from exec session timeout). Re-run completed clip 3 in 123.4s with full cache.
- **Cost: $2.89** — driven by large system prompt (182K tokens) × 21 LLM turns (cache reads dominate).
- CDN result: https://cdn.pika.art/v2/files/agent/5de4c26e-8349-40ce-bffd-863b8446daf8/bench_ltsv_run1_result.json
