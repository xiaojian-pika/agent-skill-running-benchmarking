# Benchmark Report — music-video / Claude Code / Sonnet 4.6 / Run 1

**Platform:** claudecode  
**Date:** 2026-04-13  
**Wall time:** 13m 27s (807.1s)  
**Song:** APT. — ROSÉ & Bruno Mars (30s Apple Music preview)  
**Engine:** Minimax Hailuo-2.3-Fast (i2v) + LTX-2.3 (lipsync)  
**Output:** 9 clips, 29.95s, 1080×1920, 38.4MB, karaoke captions  
**CDN:** https://cdn.pika.art/v2/files/agent/87844656-267f-4de6-865e-cb5f1ac39e43/final.mp4

---

## Phase Breakdown

| Phase | Wall time | % of total |
|-------|-----------|------------|
| Asset acquisition (Apple Music) | 3.6s | 0.4% |
| Shot script gen (LLM) | 35.3s | 4.4% |
| Character ref gen (Gemini) | 23.9s | 3.0% |
| Keyframe gen (Gemini × 9) | 171.9s | 21.3% |
| **Parallel video gen** (3 workers) | **346.0s** | **42.9%** |
| Assembly (normalize+concat+mix) | 28.5s | 3.5% |
| Captions (Whisper + ffmpeg) | 73.0s | 9.0% |
| CDN upload | 10.0s | 1.2% |
| LLM overhead (coord/worker) | 114.9s | 14.2% |

## Token Usage

| Token type | Count |
|------------|-------|
| input_tokens | 59 |
| output_tokens | 43,084 |
| cache_read_tokens | 2,975,786 |
| cache_write_tokens | 54,849 |
| **effective_input_tokens** | **3,030,694** |
| total_tokens | 3,073,778 |

Cache hit rate: 98.2% of effective input came from cache reads.  
**Estimated cost: $1.74** (Sonnet 4.6 pricing)

## Key Observations

1. **Parallel video gen dominates wall time (42.9%)** — 3 workers ran concurrently; longest worker (W1, Minimax) took ~222s. Bottleneck is external API latency (Minimax ~70s/clip).

2. **Keyframe gen is unexpectedly expensive (21.3%)** — 9 sequential Gemini API calls took 171.9s. This could be parallelized to reduce to ~30-40s with concurrent calls.

3. **LLM overhead is relatively low (18.6%)** — Shot script gen (35.3s) + worker coordination overhead (~115s). Claude Code significantly outperforms PikaBot expected overhead here (no 106K system prompt).

4. **Captions surprisingly fast (73s)** — faster-whisper on CPU for 30s audio with karaoke style. Includes Korean language detection and CJK font loading.

5. **Cache dominates token cost** — 96.8% of effective input tokens were cache reads (prompt caching working well). Output tokens (43K) from 3 worker subagents + coordinator drive the output cost.

## Known Issues / Caveats

- **Engine mismatch:** Benchmark used Minimax, not Kling (SKILL.md default). Correct path is: Kling direct → `kling_via_fal` fallback. A separate run should test Kling engine.
- `socksio` was missing at run start — installed at runtime (minor 434ms penalty on character_ref_gen first call).
- `parallel_video_gen` wall time includes worker subagent LLM coordination overhead (not separable).
- Token count includes 37 messages filtered outside the benchmark window (pre-existing session context).

## Recommendations

- **Parallelize keyframe gen** — most time-reducible optimization (could save ~130s)
- **Test Kling engine** as a separate run_2 (expected: significantly longer per-clip time, higher quality)
- **Compare vs PikaBot** once PikaBot music-video run is available
