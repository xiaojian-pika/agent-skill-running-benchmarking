# Benchmark Report — music-video / claudecode / Sonnet 4.6 / Run 2

**Platform:** claudecode
**Date:** 2026-04-13
**Wall time:** 16m17s (977.2s) — video gen forward only (asset/keyframe phases reused from run1)
**Song:** APT. — ROSÉ & Bruno Mars (30s Apple Music preview)
**Engine:** Kling via `kling_via_fal` (fal-ai/kling-video/o3/pro/reference-to-video) + LTX-2.3 lipsync
**Output:** 9 clips, 29.95s, 1080×1920, 41.7MB, karaoke captions
**CDN:** https://cdn.pika.art/v2/files/agent/fadc23c6-1011-4562-923a-3e2d7621b468/final2.mp4

---

## Phase Breakdown (run2 only — excludes reused phases)

| Phase | Wall time | % of total |
|-------|-----------|------------|
| Setup + audio seg extract | 38.0s | 3.9% |
| **Parallel video gen (Kling FAL × 6 + LTX × 3)** | **862.7s** | **88.3%** |
| Assembly (normalize+concat+mix) | 18.0s | 1.8% |
| Captions (Whisper + ffmpeg) | 26.8s | 2.7% |
| CDN upload | 10.1s | 1.0% |
| LLM overhead (coord + error handling) | 21.6s | 2.2% |

---

## Run1 vs Run2 — Engine Comparison

| Metric | Run1 (Minimax) | Run2 (Kling FAL) | Δ |
|--------|---------------|-----------------|---|
| parallel_video_gen wall | **346.0s** | **862.7s** | +149% |
| Avg time / i2v clip (6 clips) | ~73s | ~225s | +208% |
| Avg time / lipsync clip (3 clips) | ~54s | ~53s | ≈ same |
| Assembly | 28.5s | 18.0s | -37% |
| Captions | 73.0s | 26.8s | -63% (cached whisper) |
| Output size | 38.4MB | 41.7MB | +9% |
| LLM overhead % | 18.6% | 5.4% | -13pp |
| Total wall (full e2e) | ~807s | ~1208s (est w/ keyframes) | +50% |
| Token cost | $1.74 | $2.05 | +18% |

---

## Token Usage

| Token type | Count |
|------------|-------|
| input_tokens | 34 |
| output_tokens | 29,388 |
| cache_read_tokens | 2,583,487 |
| cache_write_tokens | 222,682 |
| effective_input_tokens | 2,806,203 |
| total_tokens | 2,835,591 |

Higher `cache_write` vs run1 (222K vs 55K): workers generated more output tokens logging Kling API errors and fallback attempts.

**Estimated cost: $2.05** (vs $1.74 run1, +18%)

---

## Key Findings

1. **Kling direct API unavailable** — HTTP 429 code 1102 "Account balance not enough" on all 6 character/empty/broll clips. All fell back to `kling_via_fal` (FAL AI hosted Kling).

2. **Kling FAL is 3× slower than Minimax** — avg 225s/clip vs 73s. This matches SKILL.md estimates (Kling 10-15 min/clip vs Minimax 3-5 min/clip). Kling clips are higher quality (7-17MB each vs 1-8MB for Minimax).

3. **LTX-2.3 lipsync unchanged** — consistent ~50-56s regardless of engine choice (FAL infrastructure, not Kling). This is the most efficient clip type.

4. **Worker reliability issue** — W1 agent hit stream idle timeout (~9.5 min). clip_003 had to be retried on main thread, adding ~146s to wall time. Kling's longer generation time makes worker timeouts more likely.

5. **Kling clip quality noticeably higher** — files are 2-10× larger (7-17MB vs 1-8MB), suggesting higher bitrate / richer motion. Worth the time cost for final production.

## Recommendations

- **Set worker timeout > 15 min** for Kling engine (current default too short)
- **For speed:** use Minimax (~14 min total for 30s preview)
- **For quality:** use Kling (~16-20 min total for 30s preview, higher output quality)
- **Add Kling balance check** at intake — if balance < threshold, warn user and offer Minimax as alternative
- **Lipsync (LTX-2.3) is engine-agnostic** — keep as fixed path regardless of i2v engine
