# Benchmark Report: long-to-short-video — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** T1 fresh 3-clip tiktok, T2 cache-hit rerun, T3 hormozi style fresh, T4 5-clip fresh
**Content:** Matt Cutts "Try Something New for 30 Days" (YouTube, 3m27s / 8MB h264)
**Cost:** $1.0432 (CC orchestration overhead across 2 sessions; skill S3 LLM via Anthropic proxy not in JSONL)
**Result:** SUCCESS — all 4 tasks completed (T3/T4 required rerun after initial dc_solutions 403 failure)

## Timing Summary

| Step | Duration | Notes |
|------|----------|-------|
| T1 — fresh 3 clips (tiktok) | **340.709s** | s1_apify=50s s1_dl=2s s2=10s s3=11s; 3 clips |
| T2 — cache hit | **0.196s** | All stages cached; instant |
| T3 — fresh 3 clips (hormozi) | **371.103s** | s1_apify=50s s2=9s s3=10s; 3 clips |
| T4 — fresh 4/5 clips (tiktok) | **412.317s** | s1_apify=36s s2=11s s3=15s; 4 clips returned |
| **Total tool calls** | **1124.325s** | |
| **CC LLM overhead** | **0.030s** | two bash calls, measurement noise |
| **Wall total** | **1124.355s** | |

- CC LLM overhead: **~0%** (two separate bash calls, each single-session)
- Skill execution: **~100%** of wall time
- T3/T4 first attempts failed (dc_solutions 403 → scraper_one AV1 no audio; ~142s excluded)

## Results per Test Case

### T1 — fresh 3 clips (tiktok, 340.709s)
- **S1:** dc_solutions SUCCEEDED in 50s → 8MB h264 downloaded in 2s
- **S1 face timeline:** ~20s (h264, 207s video, OpenCV; 8× non-critical mmco warnings)
- **S2 Whisper:** 482 words in 10s
- **S3 LLM:** 3 clips selected in 11s; virality [8.7, 7.8, 5.0]
- **S4-S7:** ~83s avg per clip (×3 = ~249s); clips uploaded to CDN
- **Clip 1 (8.7):** 91.0–136.4s "you can do anything for 30 days" → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/a238b90f-ef7b-4c61-9bda-76848f364146/clip_01_final.mp4)
- **Clip 2 (7.8):** 152.0–197.0s "small sustainable changes more likely to stick" → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/f147153d-be81-4b93-89fb-61ff17b0eb2f/clip_02_final.mp4)
- **Clip 3 (5.0):** 0.0–45.0s (gap-fill fallback, 1s intro trimmed) → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/7a8e59af-538e-47da-85a0-023aaf53c262/clip_03_final.mp4)

### T2 — cache hit (0.196s)
- S1 video cache hit, face timeline from cache (104 samples), transcript from cache, all 3 clips from checkpoint — S4-S7 skipped entirely. No re-upload.
- Confirms f4f6db0 caching working correctly.

### T3 — fresh 3 clips (hormozi, 371.103s)
- **S1:** dc_solutions SUCCEEDED in 50s → 8MB h264 in 0s (hosted download)
- **S2 Whisper:** 483 words in 9s
- **S3 LLM:** 3 clips in 10s; virality [8.7, 7.2, 5.0]
- **S4-S7:** ~94s avg per clip (×3 = ~282s) — slightly slower than T1 (~83s); clip 1 is longer (59.2s vs 45.4s) due to hormozi boundary
- **Clip 1 (8.7):** 91.0–150.2s (longer cut for hormozi style) → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/151dec10-74ca-4ff5-b2ca-767466d5a604/clip_01_final.mp4)
- **Clip 2 (7.2):** 152.0–197.2s → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/088e66a6-04f8-4e67-9827-e880051cbdb4/clip_02_final.mp4)
- **Clip 3 (5.0):** 0.0–45.0s (gap-fill) → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/7e2984d3-3ba0-48bf-8322-b0d4ee51e72c/clip_03_final.mp4)

### T4 — 5 clips requested, 4 returned (tiktok, 412.317s)
- **S1:** dc_solutions SUCCEEDED in 36s → 8MB h264 in 0s
- **S2 Whisper:** 482 words in 11s
- **S3 LLM:** 4 clips selected in 15s (requested 5); virality [8.7, 7.6, 5.0, 5.0]
- **S4-S7:** ~83s avg per clip (×4 = ~332s); 4 clips uploaded
- **Note:** LLM found 4 viable segments; pikabot returned 3 on same video — model non-determinism. Clips 3+4 are gap-fill fallbacks.
- **Clip 1 (8.7):** 91.0–136.4s → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/b5a3f2e6-6702-47d2-a408-5a3a09640d49/clip_01_final.mp4)
- **Clip 2 (7.6):** 152.0–195.6s → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/e3d8ae48-4bbe-454a-b059-85314bf1c12c/clip_02_final.mp4)
- **Clip 3 (5.0):** 0.0–45.0s (gap-fill) → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/b7e86138-fab8-45e8-8d3f-c61e351185ef/clip_03_final.mp4)
- **Clip 4 (5.0):** 45.0–90.0s (gap-fill, start snapped to 48s past no-face interval) → [CDN](https://msaocnoosm1a4.pika.art/v2/files/agent/84941f2b-3cdb-4aa1-8ebc-a2749892deff/clip_04_final.mp4)

## Observations

- **T3/T4 first attempts failed (dc_solutions 403 → scraper_one AV1):** dc_solutions actor succeeded but the signed YouTube URL it returned was IP-bound to the Apify server. Downloading from the devbox → 403. Fallback to scraper_one returned AV1 video-only (no audio stream) → S2 failed. Re-run resolved it: dc_solutions returned a hosted (not IP-bound) URL. This is intermittent actor behavior, not a skill bug.

- **S4-S7 per-clip dominates wall time:** T1/T4 ~83s/clip, T3 ~94s/clip (longer clip). Across T1+T3+T4 = 10 clips × ~85s avg = ~850s of the total 1124s (76%). Parallelizing clip processing would be the biggest wall-time improvement.

- **Devbox faster than pikabot for S4-S7:** ~83s/clip vs pikabot's ~121s/clip. Same h264 input, same codec. Devbox likely has faster CPU for OpenCV face detect + ffmpeg reframe.

- **T2 cache hit 0.196s (pikabot 0.184s):** Both platforms essentially instant. f4f6db0 cache validated.

- **Apify S1 timing consistent:** T1=50s, T3=50s, T4=36s (range 36–50s). Consistent with pikabot (36–52s). Apify actor itself is the bottleneck, not network.

- **hormozi vs tiktok clip boundaries differ:** T3 clip 1 is 59.2s (91–150.2s) vs T1/T4 clip 1 at 45.4s (91–136.4s). hormozi style selects a longer clip for the same segment — consistent with the style's preference for more context.

- **T4 clips_returned=4 vs pikabot's 3:** Same video, same model, both fresh LLM calls — model non-determinism on the boundary between "viable" and "gap-fill" for a 3m27s source. 2 of 4 clips are gap-fills (score 5.0) in both cases.

- **Clip 1 virality=8.7 consistent across all runs:** T1/T2/T3/T4 all select 91–136s as the top segment (score 8.7). The "novel confession" segment is deterministically the strongest clip in this video.
