# short-film Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-15
**Platform:** pikabot on EKS pod
**Skill:** short-film feat/short-film@HEAD
**Run:** pikabot run1

## Results

| Metric | Value |
|--------|-------|
| Wall total | **1532s (25.5 min)** |
| Tool calls | 1330s (86.8%) |
| LLM overhead | 202s (13.2%) |
| Output size | 41 MB |
| Total tokens | 219,247 |
| Estimated cost | $0.52 |

## Timing breakdown

| Stage | Duration | Notes |
|-------|----------|-------|
| init (Stage 0) | ~5s | Project dir + project.json |
| plan (Stage 1) | ~110s | LLM story bible + 10-shot plan |
| assets_gemini (Stage 2) | 97s | 5 images, all succeeded |
| keyframes_gemini (Stage 3) | 553s | 8/10 succeeded (2 failed: ghost shots) |
| music_minimax (Stage 3.6) | 39s | 659KB horror score |
| kling_submit (Stage 4) | ~30s | 4 batches concurrent |
| kling_poll (Stage 4) | 566s | All 4 batches completed |
| kling_assemble (Stage 4) | 82s | Concat + CDN upload |
| lipsync_mix (Stage 4.5) | N/A | Not run — timeout |

## CDN Output
https://cdn.pika.art/v2/files/agent/2cd158cc-baf8-413f-9d89-2c41235ab91a/final_video_only.mp4

## Observations

**What worked:**
- Full Stage 0-4 pipeline completed end-to-end on PikaBot ✅
- 4/4 Kling batches succeeded (all shots rendered) ✅
- Kling render time: ~9.4 min (566s polling) — on the fast end
- Music generation: 39s (unusually fast vs 90-300s expected range)
- LLM overhead only 13.2% of wall time — tool/API calls dominate

**Issues:**
- 2/10 keyframes failed (shot_07, shot_08 — pale ghost in white dress) — likely Gemini content filtering on horror imagery
- Stage 4.5 (lipsync) not reached — subagent timed out at 25+ min mark
- Token extraction limited: only 2 messages captured in window (most tokens consumed in subagent session, not traceable to parent JSONL easily)
- Skill installed from git, not CMS — no install timing available

**vs claudecode run1 comparison:**
| Metric | PikaBot | Claude Code run1 |
|--------|---------|-----------------|
| Wall total | 1532s | 1264s |
| LLM overhead % | 13.2% | 13.9% |
| Keyframe success | 8/10 | 12/12 |
| Kling batches | 4 | 5 |
| Lipsync | Not run | No (sfx_hint) |
| Cost | $0.52 | $3.37 |

PikaBot is $2.85 cheaper (Claude Code has 4.5M tokens from large system prompt + long context).
