# music-video Benchmark — pikabot / claude-sonnet-4-6
**Date:** 2026-04-13
**Platform:** PikaBot (EKS pod)
**Model:** claude-sonnet-4-6
**Skill:** music-video (feat/music-video branch)
**Outcome:** ✅ Success

---

## Summary

Full e2e 30-second music video generated from Apple Music preview. 7 clips: 2× empty, 2× lipsync (ltx-2.3), 2× character, 1× broll_instrument. Karaoke captions burned. Total wall time ~163 min — dominated by sequential clip generation and LLM polling overhead.

**Output:** https://cdn.pika.art/v2/files/agent/15ef940e-6359-4891-a7c5-e0e3cbbac91a/final.mp4

---

## Results

| Metric | Value |
|--------|-------|
| Wall total | **9749s (~163 min)** |
| Tool calls | 1056s (10.8%) |
| LLM overhead | 8693s (89.2%) |
| Output size | 38.9MB |
| Total tokens | 6,327,288 |
| Estimated LLM cost | $8.797 |

---

## Phase Timing

| Phase | Time |
|-------|------|
| install | 0s (pre-installed) |
| audio_acquisition | 1s |
| shot_script_generation (LLM) | 8s |
| keyframe_generation (7× Gemini) | 168s |
| clip_001 empty (fal kling) | 150s |
| clip_002 lipsync (ltx-2.3) | 49s |
| clip_003 broll (fal kling) | 165s |
| clip_004 character (fal kling) | 185s |
| clip_005 empty (fal kling) | 109s |
| clip_006 lipsync (ltx-2.3) | 48s |
| clip_007 character (fal kling) | 130s |
| normalize + concat | 58s |
| audio mix | 1s |
| karaoke captions | 28s |
| upload | 8s |
| **Total tool calls** | **1056s** |

---

## Per-Clip Timings

| Clip | Type | Engine | Time | Size |
|------|------|--------|------|------|
| 001 | empty | fal kling o3/pro | 150s | 10.1MB |
| 002 | lipsync | ltx-2.3 | 49s | 3.1MB |
| 003 | broll_instrument | fal kling o3/pro | 165s | 4.4MB |
| 004 | character | fal kling o3/pro | 185s | 1.8MB |
| 005 | empty | fal kling o3/pro | 109s | 9.5MB |
| 006 | lipsync | ltx-2.3 | 48s | 1.0MB |
| 007 | character | fal kling o3/pro | 130s | 18.0MB |

**ltx-2.3 is ~3× faster than kling** (49s vs 150s avg) for lipsync clips.

---

## Token Cost Analysis

| Token Type | Count | Price | Cost |
|------------|-------|-------|------|
| input | 44 | $3/M | ~$0.00 |
| output | 15,615 | $15/M | $0.23 |
| cache_read | 4,378,529 | $0.30/M | $1.31 |
| cache_write | 1,933,100 | $3.75/M | $7.25 |
| **Total** | **6,327,288** | | **$8.80** |

**Key finding:** cache_write (1.9M tokens × $3.75/M = $7.25) is the dominant cost driver. This is the 106K system prompt being written to cache on every turn (~18 turns × 106K = 1.9M). Each new session forces a cache write, making PikaBot expensive for long multi-turn benchmark tasks.

---

## Architecture Observations

### 1. FAL_KEY not in default PikaBot environment
`FAL_KEY` is required for all fal.ai calls (kling + ltx-2.3). It is NOT auto-provided by PikaBot — must be injected via `env.vars` config or provided by user. Without it, clip generation phase is completely blocked.

### 2. Sequential vs parallel clip generation
This benchmark ran clips sequentially (1 at a time in main session). The skill's production design spawns N parallel worker subagents. Parallel execution would reduce wall time from 836s to ~185s (bottlenecked by slowest clip).

### 3. LLM overhead = 89.2%
Almost entirely from polling delays between clip generation tool calls. With parallel workers, LLM overhead would drop to ~30-40%.

### 4. ltx-2.3 lipsync performance
- Average: **48.5s per clip** (4-5s clips)
- Much faster than kling (avg 148s for non-lipsync)
- Quality: acceptable for short lipsync segments, mouth movement visible
- Single-step (image + audio → video) — no intermediate base video needed

### 5. Kling o3/pro variance
- Range: 109s–185s (high variance)
- Larger output files tend to take longer (18MB clip took 130s; 1.8MB took 185s — no clear correlation with size)
- Queue wait time is the dominant variable

### 6. Keyframe generation cost
- 7 keyframes via Gemini: 168s total (~24s/frame)
- All 9:16 portrait format, avg 1.6MB each
- Consistent quality, no failures

---

## Issues Found

1. **clip_004 timing error**: `fal_poll` returned early but file was generated. Likely a status URL race condition in the polling loop. File exists (1.8MB) and is valid.
2. **clip_006 small output (1.0MB)**: ltx-2.3 generated a valid 5s clip but lower bitrate than expected. May need `guidance_scale` tuning.
3. **SSL warnings**: All fal.ai calls produce `InsecureRequestWarning` (verify=False). Should add cert bundle or use `certifi`.

---

## Recommendations

1. **Inject FAL_KEY** into PikaBot env.vars config for agents that use music-video skill
2. **Use coordinator+worker architecture** for production runs (reduces wall time from 163min → ~30min for 30s MV)
3. **Benchmark parallel run** as run2 to measure real production performance
4. **ltx-2.3 is preferred** over kling for lipsync: 3× faster, cheaper, single-step
