# Benchmark Report: viral-trend-finder on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** T1 find fitness (TikTok+IG), T2 find cooking (X), T3 analyze Instagram Reel, T4 trending general
**Session:** sesn_011CZvDUmT73191dPWN2K1Mf

## Results

| Metric | Value |
|--------|-------|
| Wall total | **447.4s** |
| Tool execution (parallel-adjusted) | 388.4s (86.8%) |
| LLM overhead | 59.0s (13.2%) |
| Tokens (total) | 79,338 |
| Estimated cost | $0.119 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Initial LLM (read task + dispatch) | — | 17.7s | 17.7s |
| T1+T2+T4 parallel dispatch (sequential container) | 92.7s | 4.7s | 97.4s |
| Workspace check (T1 failed → confirm VTF installed) | 2.1s | 11.2s | 13.3s |
| T1 re-run | 21.2s | 8.8s | 30.0s |
| T3 nohup launch | 1.0s | 5.5s | 6.5s |
| T3 poll (265.9s T3 + 19 polls×15s overhead) | 271.6s | 11.9s | 283.5s |

## Per-Script Timing

| Test | Script total | Platform | Result count | Notes |
|------|-------------|----------|--------------|-------|
| T1 @fitness (TikTok+Instagram) | 20.2s | tiktok+instagram | 11 results | Re-run after init race |
| T2 @cooking (X/Twitter) | 5.5s | x | 10 results | Single-platform, fastest |
| T3 analyze (Instagram Reel) | 265.9s | instagram | 9 shots, 165 frames | CDN fallback, 19 Gemini batches |
| T4 trending (all platforms) | 82.4s | multi | 10 results | 5 categories × 3 platforms |

## T3 Sub-Stage Breakdown (inferred from stderr)

| Sub-stage | Duration (est.) | Notes |
|-----------|----------------|-------|
| Metadata fetch | ~5s | API metadata + yt-dlp attempt |
| Video download | ~30s | yt-dlp failed on IG auth; Apify CDN fallback, 38.2MB |
| Frame extract | ~3s | ffmpeg 1fps, 165 frames from ~165s video |
| Gemini Vision | ~162s | 19 parallel batches; last batch done at t=162s; 1/19 failed |
| LLM synthesis | ~66s | Anthropic LLM via Pika proxy |

## Key Observations

- **VTF skill installed via init_script:** Environment `pika-vtf-env` runs a Python init_script that downloads VTF v1.0.6 from Pika skill hub at container startup. nova3-common is mounted as a skill bundle. Both were available before T2/T4/T1-rerun ran.

- **T1 first attempt failed (init race condition):** T1+T2+T4 were dispatched simultaneously at t=17.7s. T1 ran immediately and hit "No such file or directory" — the init_script was still writing VTF files. T2 and T4 ran after init completed and both succeeded. Agent detected the failure, confirmed VTF was installed, and re-ran T1 successfully.

- **Parallel dispatch, sequential container execution:** Agent dispatched T1+T2+T4 simultaneously (same timestamp); all three results returned at t=110.2–110.4s. Container ran them sequentially (T1_fail→T4→T2 order, total script execution = 0.066+82.4+5.5 = 88s + ~4.7s overhead = 92.7s wall).

- **T3 required nohup+poll:** analyze with full Gemini Vision pipeline takes 265.9s (4.4 min), well over the 295s bash timeout. nohup+background+poll pattern worked correctly. Agent polled at poll 19 (~285s after launch).

- **T3 Instagram CDN fallback:** yt-dlp failed on Instagram authentication (expected for private/auth-required). VTF automatically fell back to Apify CDN endpoint and downloaded the 38.2MB video successfully.

- **Gemini Vision: 19 batches in parallel, 162s:** 165 frames batched into 19 groups, all analyzed concurrently. Last batch done at t=162s from Gemini start. 1/19 batches failed (auto-degraded, not fatal).

- **Fastest test is X/Twitter find (5.5s):** Single-platform RapidAPI search. Instagram find (20s) is slower due to Apify. T4 trending at 82.4s is the slowest find test (15 yt-dlp/API calls across 5 categories × 3 platforms).

- **llm_pct = 13.2%** — consistent with other MCA media-processing skills (video-captions: ~31%, video-translation: ~31%). Lower than video skills because T3 (largest component at 265.9s) is dominated by external API calls (Gemini, CDN download) with no in-session LLM overhead.

- **Cost: $0.119** — reasonable for the complexity. Mostly cache_read (65K tokens), suggesting the system prompt + skill context was heavily cached.
