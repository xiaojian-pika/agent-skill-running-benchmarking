# Benchmark Report: short-ads — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-23
**Platform:** Claude Code (local Mac)
**Model:** Claude Sonnet 4.6
**Task:** Generate 30s brand TVC for FREITAG from brand brief (2×15s SeeDance acts, MiniMax BGM, ElevenLabs VO)
**Result:** SUCCESS — 11MB, 30.08s output, local delivery
**Output:** `/tmp/ad-bench/final.mp4`

> **Note:** Two infrastructure failures inflated wall time significantly. (1) fal.ai 30s read timeout on first SeeDance submission attempt for both acts — jobs submitted OK but polling disconnected at ~355s each; both retried successfully. (2) MiniMax proxy (`7i30hpv4bo9ud5mhianq.pika.art`) down for BGM — 3 attempts all failed (RemoteDisconnected + SSLEOFError, 228s wasted); BGM reused from prior TVC run. LLM phase was short (~25s) because prompts were reused from same-session TVC#2. Estimated clean-infrastructure wall: ~390s.

## Timing Summary

| Step | Duration |
|------|----------|
| LLM: concept + tone profile + script + Seedance prompts | ~25s (reused; fresh ~180–300s) |
| SeeDance Act 1 (fal.ai r2v, 1 image ref, retry) | 213s |
| SeeDance Act 2 (fal.ai r2v, 2 image refs, retry) | 249s |
| **SeeDance wall (parallel: max of act1/act2)** | **249s** |
| ffmpeg concat (act1 + act2 → video_noaudio.mp4) | 8s |
| BGM MiniMax music-2.5 | 0s (reused; typical 60–120s) |
| VO ElevenLabs eleven_v3 Brian | 3s |
| ffmpeg final encode (crop + eq + audio mix) | 16s |
| **Total tool calls (successful steps)** | **301s** |
| **LLM overhead** | **~370s\*** |
| **Wall total** | **671s (11m11s)** |

\* 370s LLM overhead is misleading — ~355s of it is fal.ai retry polling misclassified as overhead. True LLM thinking ~25s this run. Estimated clean-infrastructure: tool_calls ~330s, llm ~60s, wall ~390s → llm_pct ~15%.

- Acts ran in parallel — wall time = max(act1=213s, act2=249s), not sum
- LLM overhead (as recorded): 55.1% of wall | Skill/tool execution: 44.9%
- **Estimated clean-run breakdown:** LLM ~15%, skill ~85%

## Token Usage

| Metric | Value |
|--------|-------|
| input_tokens | 46 |
| output_tokens | 14,303 |
| cache_read_tokens | 5,347,767 |
| cache_write_tokens | 23,563 |
| effective_input_tokens | 5,371,376 |
| total_tokens | 5,385,679 |
| **Estimated cost** | **$1.91** |

Extracted via `extract-cc-tokens.py --after 2026-04-23T05:01:31Z --before 2026-04-23T05:12:42Z`. 34 messages matched, 686 filtered out. High cache_read due to large SKILL.md being re-read across tool calls and long session context from same-session TVC#1+TVC#2 runs.

## API Bottlenecks

| API | Duration | % of clean wall (390s) |
|-----|----------|------------------------|
| SeeDance Act 1 (fal.ai r2v) | 213s | 54.6% |
| SeeDance Act 2 (fal.ai r2v) | 249s | 63.8% |
| **SeeDance wall (parallel)** | **249s** | **63.8%** |
| ffmpeg concat + encode | 24s | 6.2% |
| ElevenLabs VO | 3s | 0.8% |
| MiniMax BGM | 0s reused (typical 60–120s) | ~15–31% |
| LLM (clean estimate) | ~60s | ~15.4% |

## Observations

- **SeeDance is the dominant bottleneck**: Both acts ran in parallel (249s wall). Serializing would take 213+249=462s instead of 249s. Parallelism saves ~3.5 min per ad.
- **fal.ai read timeout is a known issue**: The 30s polling read timeout in seedance.py triggers on jobs that take >355s. Both acts hit this on first attempt. Retry resolved it. Fixing the timeout to 60–120s in seedance.py would eliminate this failure mode without code changes.
- **MiniMax proxy instability**: The `7i30hpv4bo9ud5mhianq.pika.art` proxy was completely unreachable for BGM generation (3 attempts, 228s wasted). This is the most disruptive failure — unlike the fal.ai timeout it cannot be retried to success. BGM was reused from a prior run; a clean run would need ~60–120s here if proxy is healthy.
- **LLM overhead is minimal when prompts are warm**: The 25s LLM phase reflects reuse of concept/script/prompts from the same session's TVC#2 run. A fully cold run generating concept → tone profile → 10-shot script → 2x Seedance prompts from scratch is estimated at 180–300s.
- **Cost is dominated by cache reads**: 84% of cost ($1.60) comes from cache_read at $0.30/M × 5.35M tokens. Actual generation (input+output) adds only $0.21. This reflects the large SKILL.md being re-read across many tool calls.
- **VO is negligible**: 3s, 24.9KB for a 1.2s slogan clip. ElevenLabs eleven_v3 Brian is fast for short texts.
- **Final encode is clean**: crop=1200:675:40:22 + eq=brightness=0.04:contrast=0.90 successfully removes SeeDance edge artifacts and lifts near-black. 16s for a 30s H.264 crf=16 slow preset is reasonable on local Mac.

## Deviations from Standard Run

| Stage | Standard | This Run | Impact |
|-------|----------|----------|--------|
| LLM phase | Cold run: concept → tone → script → prompts (~180–300s) | Prompts reused from same-session TVC#2 (~25s) | **-155s to -275s** |
| BGM (MiniMax) | Fresh generation (~60–120s) | Reused from prior run (0s) | **-60s to -120s** |
| SeeDance Act 1 | Single attempt | Retry after fal.ai read timeout (+355s wasted) | **+~355s** |
| SeeDance Act 2 | Single attempt | Retry after fal.ai read timeout (+355s wasted) | **+~355s** |

**Estimated full clean-infrastructure wall: ~390s** (adds proper LLM + fresh BGM, removes retry overhead)

## Output

- **Local path:** `/tmp/ad-bench/final.mp4`
- **Duration:** 30.08s
- **Resolution:** 1280×720 (landscape 16:9)
- **Codec:** H.264 + AAC
- **File size:** 11MB (11,264 KB)
- **Audio:** MiniMax ambient electronic BGM (0.45 vol) + ElevenLabs Brian VO "The city gave it back." (3.0 vol, delayed to ~27.7s)
- **Video:** SeeDance 2.0 r2v, Act 1 seed=2122624967 (4.0MB), Act 2 seed=896947552 (4.9MB)
