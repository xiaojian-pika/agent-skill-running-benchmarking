# Benchmark Report: short-ads — claudecode (Sonnet 4.6) run2

**Date:** 2026-04-23
**Platform:** Claude Code (local Mac)
**Model:** Claude Sonnet 4.6
**Task:** Generate 30s brand TVC for FREITAG (run2 — fresh SeeDance, same brief as run1)
**Result:** SUCCESS — 10.8MB, 30.08s output, local delivery
**Output:** `/tmp/ad-bench-run2/final.mp4`

> **Note:** SeeDance ran cleanly on first attempt (no fal.ai read timeouts — improvement over run1). MiniMax proxy still down — BGM reused from prior run for the second consecutive time. LLM phase short (~17s) because concept+script+prompts written inline in same session context; a fully cold separate session would add ~180-300s for step-by-step LLM calls.

## Timing Summary

| Step | Duration |
|------|----------|
| LLM: concept + tone profile + script + Seedance prompts | ~17s (inline; cold session est. 180–300s) |
| SeeDance Act 1 (fal.ai r2v, 1 image ref, clean) | 267s |
| SeeDance Act 2 (fal.ai r2v, 2 image refs, clean) | 190s |
| **SeeDance wall (parallel: max of act1/act2)** | **267s** |
| ffmpeg concat (act1 + act2 → video_noaudio.mp4) | 7s |
| BGM MiniMax music-2.5 | 0s (reused; proxy failed all 3 attempts, ~200s wasted) |
| VO ElevenLabs eleven_v3 Brian | 3s |
| ffmpeg final encode (crop + eq + audio mix) | 12s |
| **Total tool calls (successful + failed BGM)** | **506s** |
| **LLM overhead** | **122s** |
| **Wall total** | **628s (10m28s)** |

- Acts ran in parallel — wall time = max(act1=267s, act2=190s)
- LLM overhead: 19.4% | Skill/tool execution: 80.6%
- **Estimated clean cold run (cold LLM + fresh BGM):** ~560–600s

## Token Usage

| Metric | Value |
|--------|-------|
| input_tokens | 16 |
| output_tokens | 12,328 |
| cache_read_tokens | 1,705,707 |
| cache_write_tokens | 20,957 |
| effective_input_tokens | 1,726,680 |
| total_tokens | 1,739,008 |
| **Estimated cost** | **$0.78** |

Extracted via `extract-cc-tokens.py --after 2026-04-23T06:38:02Z --before 2026-04-23T06:48:30Z`. 16 messages matched, 820 filtered out. Significantly cheaper than run1 ($0.78 vs $1.91) — less session context in this window, fresh cache writes instead of large cache reads.

## API Bottlenecks

| API | Duration | % of clean wall (~420s) |
|-----|----------|------------------------|
| SeeDance Act 1 (fal.ai r2v) | 267s | 63.6% |
| SeeDance Act 2 (fal.ai r2v) | 190s | 45.2% |
| **SeeDance wall (parallel)** | **267s** | **63.6%** |
| BGM MiniMax (failed, ~200s wasted) | 200s wasted | — |
| ffmpeg concat + encode | 19s | 4.5% |
| ElevenLabs VO | 3s | 0.7% |
| LLM (inline; cold est. 180–300s) | 17s | ~4% |

## Observations

- **SeeDance clean run — no timeouts**: Both acts succeeded on first submission with no read timeouts (improvement over run1 where both required retry). Act 1 took 28 polls (~267s), Act 2 took 19 polls (~190s). The fal.ai timeout in run1 appears to have been transient.
- **Act 1 slower than Act 2 despite fewer images**: Act 1 (1 image ref, 28 polls, 267s) was slower than Act 2 (2 image refs, 19 polls, 190s). fal.ai job latency is not correlated with number of reference images — it reflects queue state and model load.
- **MiniMax proxy persistently down**: Third consecutive session today (short-film run1 + short-ads run1 + short-ads run2) where `7i30hpv4bo9ud5mhianq.pika.art` fails. The single successful attempt in run1 retry1 now looks like luck. Attempt 1 this run returned a 10.3s clip (too short), then full proxy failures. The proxy needs investigation.
- **Parallel SeeDance is the key optimization**: Wall time = max(act1=267, act2=190) = 267s. If run serially: 267+190=457s. Parallelism saves ~190s = ~45% reduction in video generation time.
- **Cost dropped significantly vs run1**: $0.78 vs $1.91. The difference is almost entirely cache: run1 had 5.35M cache_read tokens vs 1.71M here. The large session context from same-day TVC#1+TVC#2 runs inflated run1's cache_read cost.
- **Encode time improved**: 12s vs 16s in run1 — same settings (crf=16 slow), slightly faster likely due to different video content complexity.

## Comparison: run1 vs run2 (same-day)

| Metric | run1 (2026-04-23) | run2 (2026-04-23) | Delta |
|--------|------------------|------------------|-------|
| Wall total | 671s | 628s | −43s |
| SeeDance Act 1 | 213s (retry) | 267s (clean) | +54s |
| SeeDance Act 2 | 249s (retry) | 190s (clean) | −59s |
| SeeDance wall | 249s | 267s | +18s |
| fal.ai timeouts | 2× (both acts) | 0× | −2 failures |
| BGM MiniMax | 0s (3× failed) | 0s (3× failed) | 0 |
| LLM phase | 25s (reused) | 17s (inline) | −8s |
| ffmpeg total | 24s | 19s | −5s |
| Estimated cost | $1.91 | $0.78 | −$1.13 |

Run2 is more representative of a clean fal.ai state (no timeouts). The cost difference is an artifact of session context size, not a real efficiency gain.

## Deviations from Standard Run

| Stage | Standard | This Run | Impact |
|-------|----------|----------|--------|
| LLM phase | Cold step-by-step tool calls (~180–300s) | Inline in active session (~17s) | **−163s to −283s** |
| BGM (MiniMax) | Fresh generation (~30–60s) | Reused (proxy down) | **−30–60s, no fresh BGM** |

**Estimated full cold-session wall: ~560–600s** (adds proper isolated LLM phase ~250s + fresh BGM ~45s, fal.ai clean)

## Output

- **Local path:** `/tmp/ad-bench-run2/final.mp4`
- **Duration:** 30.08s
- **Resolution:** 1280×720 (landscape 16:9)
- **Codec:** H.264 + AAC
- **File size:** 10.8MB (10,806 KB)
- **Audio:** MiniMax ambient electronic BGM (0.45 vol, reused 65.5s track) + ElevenLabs Brian VO "The city gave it back." (3.0 vol, delayed to ~27.3s)
- **Video:** SeeDance 2.0 r2v, Act 1 seed=1729442179 (4.3MB), Act 2 seed=41007897 (4.1MB)
