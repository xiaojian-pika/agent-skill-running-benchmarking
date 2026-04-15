# Benchmark Report: short-film — claudecode (Sonnet 4.6) run2

**Date:** 2026-04-15  
**Platform:** Claude Code (local Mac)  
**Model:** Claude Sonnet 4.6  
**Skill version:** c9ee2aa (feat/short-film — consolidated improvements)  
**Task:** Generate ~60s horror short film from 7-question creative brief (portrait 9:16)  
**Result:** SUCCESS — 46.4MB, 54.2s output, CDN delivered  
**Project ID:** film_20260415_2d271d  

> **Note:** Full run — all stages executed including Stage 2 (Gemini assets), Stage 3 (Gemini keyframes), Stage 3.6 (MiniMax music), Stage 4 (Kling 4 batches). No lipsync (sfx_hint only). Three bugs fixed during run (see Bugs section).

---

## Timing Summary

| Step | Duration |
|------|----------|
| Stage 0: init | ~0.1s |
| Stage 1: plan (write_plan()) | ~0.1s |
| Stage 2.5: script preview ⏸ user confirmation | — (user wait) |
| Stage 2: assets (Gemini, 5 parallel) | 137s (2m17s) |
| Stage 3: keyframes (Gemini, 12 sequential) | 289s (4m49s) |
| Stage 3.5: keyframe review ⏸ user confirmation | — (user wait) |
| Stage 3.6: music (MiniMax music-2.5) | 74s |
| Stage 4: video (Kling v3 omni, 4 batches) | 505s (8m25s) |
| └─ keyframe CDN upload (2 workers) | ~40s |
| └─ batch submit (4 concurrent) | ~15s |
| └─ polling (all 4 batches) | ~360s |
| └─ download + ffmpeg concat | ~90s |
| Stage 4.5: music mix + CDN upload | 12s |
| **Total tool calls** | **~1017s** |
| **LLM overhead + user pauses** | **~755s** |
| **Wall total** | **1772s (29m32s)** |

- LLM overhead (incl. user review): 42.6% of wall time
- Skill/tool execution: 57.4% of wall time

> ⚠️ Stage 3.6 ran sequentially after Stage 4 due to bug discovery/fix during run. In a clean run, 3.6 + 4 should run in parallel, saving ~74s.

---

## Token Usage

| Metric | Value |
|--------|-------|
| input_tokens | 128 |
| output_tokens | 46,254 |
| cache_read_tokens | 12,349,200 |
| cache_write_tokens | 202,270 |
| effective_input_tokens | 12,551,598 |
| total_tokens | 12,597,852 |
| **Estimated cost** | **$5.16** |

Extracted from session with 102 messages in benchmark window (1479 filtered).

---

## Comparison: run1 vs run2

| Metric | run1 (abbreviated) | run2 (full) |
|--------|-------------------|-------------|
| Stages run | 4/7 (no assets, no keyframes, no lipsync) | 7/7 |
| Wall time | 1264s (21m) | 1772s (29m) |
| Tool time | 1088s | 1017s |
| LLM% | 13.9% | 42.6%* |
| Cost | $3.37 | $5.16 |
| Tokens | 4.5M effective | 12.6M effective |

*run2 LLM% inflated by Stage 2.5/3.5 user review pauses and in-session bug fixes.

**Estimated clean full run (no bugs, no user delays):**
- Tool time: ~1017s
- LLM overhead (no pauses): ~150s
- **Total: ~1170s (~19.5 min)**

---

## API Bottlenecks

| API | Duration | % of tool time |
|-----|----------|---------------|
| Kling v3 omni (4 batches, parallel) | 360s render | 35.4% |
| Video.py total | 505s | 49.7% |
| Gemini keyframes (12 sequential) | 289s | 28.4% |
| Gemini assets (5 parallel) | 137s | 13.5% |
| MiniMax music-2.5 | 74s | 7.3% |
| Music mix + CDN upload | 12s | 1.2% |

---

## Bugs Found & Fixed During Run

| # | Bug | Fix |
|---|-----|-----|
| 1 | `keyframes.py` used hardcoded PikaBot subprocess path `/app/skills/gemini/scripts/generate-image-gemini.py` | Replaced with direct HTTP calls to PIKA proxy Gemini API (matching assets.py pattern) |
| 2 | `music.py` and `lipsync.py` missing from repo (only existed in Downloads working copy) | Copied into `short-film/scripts/` |
| 3 | `get_sender_headers` missing from `nova3_common/config.py` | Added no-op stub returning `{}` |

---

## Observations

- **Gemini keyframes now sequential, not parallel**: Unlike assets.py (ThreadPoolExecutor), keyframes.py generates shots one-by-one. With 12 shots at ~24s each, this adds ~290s. Parallelizing to 4 workers would cut this to ~75s (saving ~3.5 min).
- **Kling 4-batch parallelism works well**: All 4 batches submitted simultaneously and polled in one loop. All completed within the same polling window (~poll #9–12), total render ~6 min for 54s of video.
- **Stage 3.6 + 4 should be parallel**: In a clean run, music (~74s) overlaps with Kling render (~505s), making music generation free. The serial run here cost 74s of extra wall time.
- **cost is dominated by cache reads**: 12.4M cache_read_tokens × $0.30/M = $3.70. Larger context from SKILL.md (512 lines) + interactive stages = more tokens vs run1.
- **Interactive stages (2.5, 3.5) add unmeasured wall time**: Both pauses are working as designed — user confirmed script and approved keyframes before proceeding. These are not bottlenecks but deliberate UX gates.
- **Grid composition bug**: When retrying a single failed shot, the grid recomposes with only the newly generated shots (not all 12). Low-priority cosmetic issue.

---

## Output

- **CDN URL:** https://cdn.pika.art/v2/files/agent/5d05056b-78a5-41b0-ae93-52646da53833/final.mp4
- **Duration:** 54.2s
- **Resolution:** 1080×1920 (portrait 9:16)
- **File size:** 46.4MB
- **Audio:** Kling-native ambient SFX (sfx_hint) + horror underscore (MiniMax, 0.06 vol)
