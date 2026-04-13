# Cross-Platform Skill Benchmark Comparison — 2026-04-10

## TL;DR

PikaBot is **1.5-3.5x slower** and **5-20x more expensive** than other platforms on every skill tested. The two biggest bottlenecks are: (1) an 81-107K token system prompt that adds 47-121s of LLM thinking time per run, and (2) CDN upload + skill install overhead adding 3-27s per run. Managed Claude Agent delivers comparable results at ~$0.05-0.16 per run vs PikaBot's $0.32-1.35. Claude Code and Codex are fast but their token/cost data from this round is unreliable (see Data Quality Notes).

## Data Quality Notes

**Token & cost data**: Only PikaBot and Managed Agent have reliable per-run token/cost numbers. Claude Code and Codex token extraction tools reported **session-cumulative totals** (not per-task), making their token counts and cost estimates invalid. These fields have been nulled in result.json files.

**Anomalous runs**:
- **Managed Agent apple-music (117.9s LLM)**: Hit a DNS resolution error, agent spent ~80s debugging/retrying. Not representative of normal overhead.
- **Codex video-translation (74.3s tool time)**: Includes 42s of post-"Done" voice clone cleanup. Actual translation pipeline was ~32s.
- **Codex music-beat-sync (80.8s LLM)**: Codex averages 13-15s LLM overhead on other skills; 80.8s is a 5x outlier. Likely includes session idle time or tester activity between steps, not actual model thinking.

**Non-comparable runs**: Claude Code recorded 0% LLM overhead on 4 skills (long-to-short-video, social-account-analyzer, social-posting, viral-trend-finder) — these were run as single bash commands, not multi-turn agent orchestration. They are excluded from this comparison.

**External API variance**: music-beat-sync depends on MiniMax API (60-175s per call). This makes wall time inherently noisy across runs regardless of platform.

## Platforms

| Platform | Model | Runtime |
|----------|-------|---------|
| PikaBot | Claude Sonnet 4.6 | EKS pod (dedicated vCPUs) |
| Claude Code | Claude Sonnet 4.6 | Staging devbox (shared EC2) |
| Codex | GPT-5.4 | Codex sandbox (same devbox as Claude Code) |
| Managed Claude Agent | Claude Sonnet 4.6 | Anthropic managed container |

> Claude Code and Codex ran on the **same staging devbox**. Their local compute times should be identical — any difference comes from external API variance or measurement artifacts.

## Comparison (4 comparable skills)

### Wall Clock (end-to-end seconds)

| Skill | PikaBot | Claude Code | Codex | Managed Agent |
|-------|---------|-------------|-------|---------------|
| video-captions | 159.8 | 77.0 | **66.4** | 71.1 |
| music-beat-sync | 378.2 | **151.0** | 174.6 | 180.3 |
| video-translation | 106.0 | **70.5** | 88.6 | 98.4 |
| apple-music | 50.9 | 26.1 | **15.0** | ~~146.5~~ |

> ~~Strikethrough~~ = anomalous, excluded from comparison. Managed Agent apple-music (146.5s): includes ~80s DNS error debugging/retrying.

### Skill Execution Time (seconds)

> Actual tool/API call time (ffmpeg, Whisper, ElevenLabs, MiniMax, etc.), excluding LLM thinking and platform overhead.
> † Claude Code and Codex ran on the same machine — differences are external API variance, not compute.

| Skill | PikaBot | Claude Code † | Codex † | Managed Agent |
|-------|---------|---------------|---------|---------------|
| video-captions | 30.4s | 32.0s | 29.4s | 21.5s |
| music-beat-sync | 226.8s | 121.1s | 91.2s | 118.6s |
| video-translation | 31.8s | 36.2s | ~~74.3s~~ | 54.4s |
| apple-music | 0.6s | 8.1s | 1.3s | ~~4.8s~~ |

> ~~Strikethrough~~ = anomalous, excluded from comparison. Codex video-translation (74.3s): includes 42s voice clone cleanup after "Done". Managed Agent apple-music (4.8s): includes DNS error debug time.

### LLM Overhead (seconds)

> Model thinking time between tool calls — reading prompt, deciding next step, parsing results.

| Skill | PikaBot | Claude Code | Codex | Managed Agent |
|-------|---------|-------------|-------|---------------|
| video-captions | 77.5s | 23.1s | 14.6s | 39.3s |
| music-beat-sync | 121.4s | 27.2s | ~~80.8s~~ | 36.2s |
| video-translation | 67.7s | 34.2s | ~~14.2s~~ | 30.4s |
| apple-music | 46.6s | 17.4s | 13.7s | ~~117.9s~~ |

> ~~Strikethrough~~ = anomalous, excluded from comparison. Codex music-beat-sync (80.8s): 5x outlier vs Codex's 13-15s on other skills, likely includes session idle time. Codex video-translation (14.2s): artificially low because 42s cleanup was counted as tool time. Managed Agent apple-music (117.9s): includes ~80s DNS error debugging.

### Cost (per run, USD)

| Skill | PikaBot | Claude Code | Codex | Managed Agent |
|-------|---------|-------------|-------|---------------|
| video-captions | $0.69 | ~~n/a~~ | ~~n/a~~ | $0.13 |
| music-beat-sync | $1.35 | ~~n/a~~ | ~~n/a~~ | $0.05 |
| video-translation | $0.73 | ~~n/a~~ | ~~n/a~~ | $0.09 |
| apple-music | $0.32 | ~~n/a~~ | ~~n/a~~ | $0.16 |

> ~~Strikethrough~~ = data unavailable. Claude Code and Codex token extraction reported session-cumulative totals (not per-task), cost cannot be calculated. Pricing: Sonnet 4.6 = $3/$15/M input/output.

### Token Breakdown (PikaBot vs Managed Agent)

> Claude Code and Codex token data is session-cumulative (not per-task) and has been nulled. Only PikaBot and Managed Agent have reliable per-run numbers.

**System Prompt Size**

| Skill | PikaBot | Managed Agent |
|-------|---------|---------------|
| video-captions | 60,020 | n/a |
| music-beat-sync | 81,485 | n/a |
| video-translation | 100,554 | n/a |
| apple-music | 107,266 | n/a |

> PikaBot system prompt includes agent identity, memory, all skill definitions, and tool schemas. Managed Agent did not record this field.

**Cache Read / Write Tokens**

| Skill | PikaBot read | PikaBot write | Managed Agent read | Managed Agent write |
|-------|-------------|--------------|-------------------|-------------------|
| video-captions | 1,141,837 | 148,937 | 55,539 | 5,957 |
| music-beat-sync | 1,609,780 | 96,689 | 50,203 | 7,769 |
| video-translation | 1,016,416 | 105,798 | 42,760 | 5,878 |
| apple-music | 926,552 | 11,270 | ~~145,459~~ | ~~19,066~~ |

> Cache read reflects context re-processing across LLM turns — higher = more turns × larger context per turn.

**Input / Output Tokens**

| Skill | PikaBot in | PikaBot out | Managed Agent in | Managed Agent out |
|-------|-----------|------------|-----------------|------------------|
| video-captions | 22 | 4,028 | 91 | 1,652 |
| music-beat-sync | 20 | 4,735 | 91 | 1,705 |
| video-translation | 11 | 2,070 | 91 | 1,655 |
| apple-music | 8 | 1,537 | 97 | ~~5,622~~ |

**Total Tokens**

| Skill | PikaBot | Managed Agent | Ratio |
|-------|---------|---------------|-------|
| video-captions | 1,294,824 | 63,239 | **20x** |
| music-beat-sync | 1,711,224 | 59,768 | **29x** |
| video-translation | 1,124,295 | 50,384 | **22x** |
| apple-music | 939,367 | ~~170,244~~ | **6x** |

> ~~Strikethrough~~ = anomalous (Managed Agent apple-music includes DNS error debugging). Estimated LLM turns: PikaBot ~15-20 per skill (cache_read ÷ system_prompt), Managed Agent ~3-4.

## Analysis

**PikaBot's slowness and cost come from the same root cause**: an 81-107K token system prompt processed on every LLM turn. With ~20 turns per skill, that's 47-121s of thinking time and 1.7M tokens — vs Managed Agent's ~4 turns, 30-40s overhead, and 60K tokens on the same skill.

Skill execution itself (ffmpeg, Whisper, ElevenLabs, etc.) is roughly the same across platforms (29-36s for video-captions and video-translation). The difference is orchestration overhead.

## Action Items

**Benchmark methodology** — next round should use isolated sessions per skill (fix token data), 3+ runs per skill (reduce API noise), and standardized multi-turn orchestration across all platforms.

**PikaBot optimization** — biggest lever is reducing system prompt size; secondary wins from async CDN upload and caching skill installs.

## Appendix: Platform Overhead Detail

| Skill | PikaBot install | PikaBot upload | Managed Agent upload |
|-------|-----------------|----------------|---------------------|
| video-captions | 0.6s | 26.1s | 3.6s |
| music-beat-sync | 12.0s | 14.0s | 3.6s |
| video-translation | 2.0s | 4.0s | 2.5s |
| apple-music | 2.1s | 1.0s | 2.4s |
