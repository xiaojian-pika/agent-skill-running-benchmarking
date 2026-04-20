# Short Film Skill Benchmark — Run 3

**Date:** 2026-04-20  
**Skill:** short-film  
**Platform:** pikabot (sessions_spawn subagent)  
**Model:** claude-sonnet-4-6  
**Thinking Level:** medium  
**Session ID:** f063130f-5806-4032-adb5-acba70d5ba3c  
**Git Commit:** 63c7b9d

## Prompt

Generate a short film about a young woman saying goodbye to her childhood home in spring. The cherry blossoms are falling. She is in her mid-20s, nostalgic, bittersweet. Portrait 9:16, soft cinematic style, warm natural light.

## Result

**Status:** ✅ success — full pipeline completed  
**Title:** *Sayonara* — A Farewell to Childhood  
**CDN URL:** `https://cdn.pika.art/v2/files/agent/78f48cb8-2368-435a-884e-2ca3d0139f1c/final_video_only.mp4`  
**Shots:** 8  
**Duration:** 40.2s  
**File Size:** 33 MB  
**Orientation:** 9:16 portrait  
**Style:** Soft cinematic, muted pastels, warm natural light

## Timing

| Metric | Value |
|---|---|
| T_START | 2026-04-20T06:20:12.616Z |
| T_END | 2026-04-20T06:33:36.000Z |
| Wall time | 791.5s (13m 12s) |
| LLM overhead | 152.6s (19.3%) |
| Tool/API time | 639.0s (80.7%) |

## LLM Dimension

| Metric | Value |
|---|---|
| LLM calls | 20 |
| Mean call duration | 7.6s |
| p95 call duration | 12.2s |
| Longest call | #5 (46.3s) — write_plan() story bible generation |
| Input tokens | 22 |
| Output tokens | 5,546 |
| Cache read tokens | 502,597 |
| Cache write tokens | 174,015 |
| Total effective tokens | 682,180 |
| System prompt tokens | 24,646 (subagent, no full PikaBot system prompt) |
| Estimated LLM cost | $0.89 |

**Call breakdown by stage:**
- Calls 1-4: SKILL.md read, prompt parse, brief confirm (18.0s)
- Call 5: write_plan() story bible, 8-shot storyboard (46.3s — dominant)
- Calls 6-8: plan finalization, scene descriptions (16.3s)
- Calls 9-11: assets.py coordination (12.0s)
- Calls 12-15: keyframes.py per-shot orchestration (16.0s)
- Calls 16-19: video.py batch coordination (20.2s)
- Call 20: final report (12.2s)

## Compute Dimension

| Stage | API Calls | Duration |
|---|---|---|
| Stage 0 — init | 0 | ~6s |
| Stage 1 — plan | 0 (LLM-only) | ~52s |
| Stage 2 — assets (Gemini Pro) | 5 | ~185s |
| Stage 3 — keyframes (Gemini) | 8 + 1 grid | ~248s |
| Stage 4 — video (Kling v3 Pro i2v) | 3 batches | ~396s |
| ffmpeg concat + upload | 1 | ~5s |

**Image model:** `gemini-3-pro-image-preview`  
**Video model:** Kling v3 Pro (image-to-video, 3 batches: 15s+15s+10s)  
**Total API call time:** 638.959s  
**API as % of wall time:** 80.7%

## Comparison vs Run 1 (Ming Dynasty epic)

| Metric | Run 1 (Apr 17) | Run 3 (Apr 20) |
|---|---|---|
| Method | Real user chat | sessions_spawn subagent |
| Shots | 16 | 8 |
| Duration | 63s | 40s |
| Wall time | 1221s | 791s |
| LLM calls | 63 | 20 |
| LLM overhead | 1103s (90.4%) | 153s (19.3%) |
| Tool/API time | 118s (9.6%) | 639s (80.7%) |
| Cache write tokens | 2,366,890 | 174,015 |
| Cost (LLM only) | $10.19 | $0.89 |
| System prompt tokens | 48,506 | 24,646 |

**Key difference:** Run 1 had 63 LLM calls with 90% LLM overhead because it ran via full PikaBot system context (multi-subagent architecture, large system prompt). Run 3 via sessions_spawn used a lighter subagent context (24K system prompt vs 48K), ran all stages inline (no sub-subagent spawning), resulting in far fewer LLM calls (20) and API-dominated wall time (80.7%).

## Notes

- **Skill installation:** short-film skill was NOT pre-installed at `/app/skills/short-film/`. Had to manually `cp` from workspace source before run. First attempt (contaminated) used gemini+kling directly without reading SKILL.md.
- **Retry count:** 1 retry due to missing skill (first subagent improvised pipeline; second used real SKILL.md)
- **sessions_spawn vs CLI:** `pikabot agent` CLI deadlocks when called from within an active gateway turn (single-threaded). `sessions_spawn` is the correct in-pod benchmarking method.
- **Sub-subagents:** Run 3 did NOT spawn sub-subagents (all stages inline). Run 1 spawned separate subagents for assets, keyframes, video — explaining its 3× higher LLM call count.
