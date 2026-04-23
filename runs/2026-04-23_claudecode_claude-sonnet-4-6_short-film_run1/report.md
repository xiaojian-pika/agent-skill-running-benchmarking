# Benchmark Report: short-film — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-23
**Platform:** Claude Code (local Mac)
**Model:** Claude Sonnet 4.6
**Task:** Generate ~60s horror short film from standard 7-question brief (portrait 9:16, cold noir, Ji-yeon ghost story)
**Result:** SUCCESS — 42.4MB, 56.2s output, CDN delivered
**Project ID:** film_20260423_6f68fe

> **Note:** This is a full run — all stages executed from scratch including fresh Gemini asset generation (run1 from 2026-04-15 reused assets). MiniMax music-2.5 returned short clips on all attempts; best was 40.0s (film is 56.2s — BGM drops out at 40s). Total music stage ~228s with retries. All other stages ran cleanly.

## Timing Summary

| Step | Duration |
|------|----------|
| Stage 0: init (project dir + project.json) | ~0s (97ms) |
| Stage 1: plan (Claude writes 12-shot story JSON) | ~200s (estimated LLM writing) |
| Stage 2: assets (Gemini, 2 chars + 3 scenes, parallel) | 30s |
| Stage 3: keyframes (Gemini, 12 shots sequential) | 222s (3m42s) |
| Stage 3.5: music (MiniMax, 3 attempts, best = 40s) | 228s (3m48s) |
| Stage 4: video (Kling v3 omni, 4 batches concurrent) | 509s (8m29s) |
| └─ Keyframe CDN upload (12 files) | ~30s |
| └─ Kling submit (4 concurrent batches) | ~20s |
| └─ Kling poll (9 × 30s, all done at poll #9) | 270s |
| └─ Download + normalize + ffmpeg concat | ~189s |
| Stage 4.5: music mix + CDN upload | 67s |
| **Total tool calls** | **~1,056s** |
| **LLM overhead (plan + inter-stage)** | **~352s** |
| **Wall total** | **1,408s (23m28s)** |

- LLM overhead: 25.0% of wall time (plan writing ~200s + coordination ~152s)
- Skill/tool execution: 75.0% of wall time
- **Estimated clean-run (single-shot music):** ~1,100s (~18% LLM, ~82% skill)

## Token Usage

| Metric | Value |
|--------|-------|
| input_tokens | 39 |
| output_tokens | 38,230 |
| cache_read_tokens | 2,618,954 |
| cache_write_tokens | 271,686 |
| effective_input_tokens | 2,890,679 |
| total_tokens | 2,928,909 |
| **Estimated cost** | **$2.38** |

Extracted from 39 messages in window (766 filtered out). Higher output tokens vs 2026-04-15 run1 (38,230 vs 25,553) because Stage 1 plan was written fresh with 12 detailed shots this run.

## API Bottlenecks

| API | Duration | % of wall |
|-----|----------|-----------|
| Kling v3 omni (4 batches, parallel) | 270s render | 19.2% |
| video.py total (upload+submit+poll+assemble) | 509s | 36.2% |
| Gemini keyframes (12 shots sequential) | 222s | 15.8% |
| MiniMax music (3 attempts, ~228s total) | 228s | 16.2% |
| Stage 4.5 mix + CDN upload | 67s | 4.8% |
| Gemini assets (2 chars + 3 scenes, parallel) | 30s | 2.1% |
| Stage 1 plan (LLM writing) | ~200s | 14.2% |

## Observations

- **Kling is still the dominant bottleneck** but now shares time with keyframe generation: video.py total (509s, 36%) vs keyframes (222s, 16%). Together they account for 52% of wall time.
- **Keyframe generation is now the second-largest bottleneck**: 12 sequential Gemini calls took 222s (~18.5s/shot). Parallelizing these would be the highest-impact optimization — potential savings of ~150-180s.
- **MiniMax music instability**: All three API calls returned short clips (9s, 40s, 19-27s). The 40s clip was accepted despite being 16s shorter than the 56.2s film. Root cause unknown — same API, same proxy, but the short-ads benchmark from earlier today also had proxy issues (`7i30hpv4bo9ud5mhianq.pika.art`). The music.py prompt derivation from `story.tone` may produce prompts that don't communicate desired duration clearly enough.
- **Gemini assets fast**: 5 images (2 chars + 3 scenes) in parallel in 30s. This stage is not a bottleneck.
- **Kling download+assemble surprisingly slow (~189s estimated)**: 4 batch MP4s totaling ~92MB (34+17+16+25MB). Download bandwidth + sequential normalize + ffmpeg concat accounts for much of the 189s gap between poll completion and stage end. Large batches (34MB for batch_1) are the likely cause.
- **No CDN upload failures**: Both final_video_only.mp4 (41MB) and final.mp4 (42.4MB) uploaded cleanly — well under the 50MB limit.
- **Cost is dominated by cache_write this run**: cache_write = $1.02 (43%), cache_read = $0.79 (33%), output = $0.57 (24%). Higher cache_write vs the April 15 run reflects writing fresh plan + keyframe outputs into cache. Cost $2.38 vs $3.37 for run1 — lower because fewer cache writes from prior session context.
- **Plan writing**: A detailed 12-shot cold noir plan took ~200s. This is in line with the benchmark estimate of 180-300s for cold starts. The plan had full character descriptions, scene image prompts, per-shot keyframe prompts, action scripts, and sfx_hints — that level of detail takes time.

## Deviations from Standard Run

| Stage | Standard | This Run | Impact |
|-------|----------|----------|--------|
| All stages | Full fresh run | Full fresh run | ±0 |
| Stage 3.5 music | Single successful API call | 3 attempts; best=40s, shorter than film | +162s wasted, music cuts out at 40s |
| Stage 4.5 lipsync | TTS + fal-ai/sync-lipsync for dialogue shots | Music mix only (sfx_hint used for dialogue) | ~−600s est. (no TTS/lipsync cost) |

**Note on lipsync:** This run used `sfx_hint` for all dialogue (the ghost's line: "You are not the first person to come to me."), so Kling generates the voice natively. A run with explicit TTS (MiniMax speech-2.8-hd) + fal-ai/sync-lipsync/v2 per dialogue shot would add an estimated 5-30min.

**Estimated full standard run with lipsync (2 dialogue shots): ~38-54 min** (same as April 15 benchmark).

## Comparison with 2026-04-15 run1

| Metric | 2026-04-15 run1 | 2026-04-23 run1 | Delta |
|--------|-----------------|-----------------|-------|
| Wall total | 1,264s | 1,408s | +144s |
| assets_gemini | ~5s (reused) | 30s (fresh) | +25s |
| keyframes_gemini | ~10s (reused) | 222s (fresh) | +212s |
| music_minimax | 182s | 228s (+retries) | +46s |
| video_kling | 762s | 509s | −253s |
| lipsync_mix | 39s | 67s | +28s |
| Output size | 40.3MB | 42.4MB | +2.1MB |
| Estimated cost | $3.37 | $2.38 | −$0.99 |

The April 15 run was slower at video (762s vs 509s) — likely Kling queue variance. This run paid an extra ~237s for fresh asset/keyframe generation compared to the reused versions. Net result: similar wall times.

## Output

- **CDN URL:** https://cdn.pika.art/v2/files/agent/85f6126c-90a9-4b69-9ff1-0955e0d3a87a/final.mp4
- **Duration:** 56.2s
- **Resolution:** 1080×1920 (portrait 9:16)
- **File size:** 42.4MB (42,424 KB)
- **Audio:** Kling-native ambient SFX + sfx_hint voice (Kling-generated) + horror ambient BGM (MiniMax, 40s, 0.06 vol — silent after 40s)
- **Video:** Kling v3 omni, 4 batches (3 shots × 14s each), all completed poll #9
