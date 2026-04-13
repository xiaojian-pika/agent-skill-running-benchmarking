# Cross-Platform Skill Benchmark — Round 2 (2026-04-11)

## Platforms

| Platform | Model | Runtime |
|----------|-------|---------|
| PikaBot | Claude Sonnet 4.6 | EKS pod (dedicated vCPUs) |
| Claude Code | Claude Sonnet 4.6 | Staging devbox (shared EC2) |
| Codex | GPT-5.4 | Codex sandbox |
| Managed Claude Agent | Claude Sonnet 4.6 | Anthropic managed container |

## Wall Clock (seconds)

| Skill | PikaBot | Claude Code | Codex | MCA | Winner |
|-------|---------|-------------|-------|-----|--------|
| video-captions | 135.7 | 28.0 | **22.9** | 77.3 | Codex |
| music-beat-sync | 324.5 | 185.9 | 133.8 | **117.8** | MCA |
| video-translation | 154.8 | 72.8 | **63.9** | 108.1 | Codex |
| apple-music | 97.0 | 16.0 | **12.8** | 138.6 | Codex |

**Codex wins 3 of 4 skills.** MCA wins music-beat-sync (likely faster MiniMax API response this run).

## LLM Overhead (% of wall time)

| Skill | PikaBot | Claude Code | Codex | MCA |
|-------|---------|-------------|-------|-----|
| video-captions | 62% | 60% | 49% | 36% |
| music-beat-sync | 30% | 12% | 10% | 31% |
| video-translation | 56% | 25% | 23% | 26% |
| apple-music | 68% | 92% | 92% | 75% |

For sub-second skills (apple-music), LLM overhead dominates on all platforms (75-92%). For compute-heavy skills (music-beat-sync), it drops to 10-31%.

## Cost (USD per run)

| Skill | PikaBot | Claude Code | Codex | MCA |
|-------|---------|-------------|-------|-----|
| video-captions | $2.49 | $0.32 | $0.94 | **$0.06** |
| music-beat-sync | $1.07 | $0.48 | $2.55 | **$0.08** |
| video-translation | $1.49 | $0.36 | $1.94 | **$0.06** |
| apple-music | $2.05 | $0.28 | $1.08 | **$0.20** |

**MCA is cheapest across all 4 skills.** PikaBot is most expensive (large system prompt = high cache token volume). Codex costs are mid-range.

Note: Codex cost uses cumulative session tokens without cache discount, making it appear higher. Claude Code and MCA costs include cache pricing.

## Round 1 vs Round 2

| Skill | PikaBot R1→R2 | CC R1→R2 | Codex R1→R2 | MCA R1→R2 |
|-------|---------------|----------|-------------|-----------|
| video-captions | 159.8→135.7 (-15%) | 77.0→28.0 (-64%) | 66.4→22.9 (-66%) | 71.1→77.3 (+9%) |
| music-beat-sync | 378.2→324.5 (-14%) | 151.0→185.9 (+23%) | 174.6→133.8 (-23%) | 180.3→117.8 (-35%) |
| video-translation | 106.0→154.8 (+46%) | 70.5→72.8 (+3%) | 88.6→63.9 (-28%) | 98.4→108.1 (+10%) |
| apple-music | 50.9→97.0 (+91%) | 26.1→16.0 (-39%) | 15.0→12.8 (-15%) | 146.5→138.6 (-5%) |

Key changes:
- **CC video-captions -64%:** Transcription switched from local faster-whisper (43s) to proxy API waterfall (~17s). Major improvement.
- **Codex video-captions -66%:** Same skill version change — API transcription much faster than local.
- **PikaBot apple-music +91%:** CMS install overhead + LLM variability. Skill itself is <5s.
- **MCA music-beat-sync -35%:** MiniMax API was faster this run (API variance, not platform improvement).

## Analysis

### Codex is the fastest platform for 3 of 4 skills

| Skill | Codex wall | Next best | Gap |
|-------|-----------|-----------|-----|
| video-captions | 22.9s | CC 28.0s | 1.2x |
| video-translation | 63.9s | CC 72.8s | 1.1x |
| apple-music | 12.8s | CC 16.0s | 1.3x |

Codex has low LLM overhead (10-49% on compute skills) and fast tool execution. GPT-5.4's per-turn thinking is fast.

### MCA is the cheapest platform

MCA costs $0.06-0.20 per run vs $0.28-2.55 for others. The managed container environment has a smaller context (no 106K system prompt like PikaBot), fewer LLM turns, and efficient caching.

### PikaBot's overhead problem persists

PikaBot is slowest on all 4 skills and most expensive on 3 of 4. The 106K system prompt drives both:
- **Speed:** 30-68% LLM overhead — each turn processes the full system prompt
- **Cost:** $1.07-2.49 per run — cache reads on every turn add up

### Video-captions got dramatically faster

The transcription waterfall change (Whisper → Deepgram → Gemini API) replaced local faster-whisper CPU inference. CC went from 77s → 28s, Codex from 66s → 23s. The bottleneck shifted from CPU (whisper) to API (transcription) + ffmpeg burn.

### MiniMax API variance still dominates music-beat-sync

Beat-sync wall times range from 117-325s across platforms, driven by MiniMax music generation (60-175s per call). This makes beat-sync benchmarks inherently noisy.

## Data Quality Notes

- Codex `total_tokens` uses platform-reported authoritative values (includes reasoning tokens)
- Codex `cache_read_tokens` is a subset of `input_tokens` (OpenAI model), not additive like Claude
- 4 MCA runs have null phase totals (warned by validator, timing exists in steps/notes)
- 1 CC run uses `apple-music` instead of `apple-music-reference` for task.name
- Some runs include aggregate + substep timings in the same `steps[]` array (not summable)
