# Benchmark Comparison: 4 Skills Across 4 Agents

**Date:** 2026-04-10  
**Inputs reviewed:** 16 benchmark runs listed in `/home/ec2-user/Benchmark/tmp.txt`  
**Reference report:** `archive/round2-full-comparison-4skills.md`

## Scope

This comparison covers 4 skills across 4 agent/runtime setups:

- `social-account-analyzer`
- `viral-trend-finder`
- `social-posting`
- `long-to-short-video`

Platforms compared:

- `pikabot` / Claude Sonnet 4.6
- `managed-claude-agent` / Claude Sonnet 4.6
- `claudecode` / Claude Sonnet 4.6
- `codex` / GPT-5.4

---

## Executive Summary

Three conclusions stand out.

1. **There is no single winner across all 4 skills.**
   - `pikabot` is fastest on `social-account-analyzer`.
   - `claudecode` is fastest on `viral-trend-finder` and `social-posting` by wall time.
   - `managed-claude-agent` is clearly fastest on `long-to-short-video`.

2. **`managed-claude-agent` is the best overall cost/performance compromise.**
   It is the cheapest platform on all 4 skills, and it wins the heaviest media skill (`long-to-short-video`) by a wide margin.

3. **`codex` is the weakest platform in this batch on price efficiency.**
   It is never the fastest, and it is by far the most expensive on all 4 skills.

A fourth point matters for interpretation: **`claudecode`'s near-zero `llm_overhead_s` is mostly a measurement artifact**, not evidence that its orchestration is inherently free. Several Claude Code runs executed all tests in a single continuous shell session, which collapses inter-step orchestration overhead almost entirely.

---

## Methodology Caveats

This dataset is useful, but it is not perfectly apples-to-apples.

### 1. Claude Code overhead is structurally understated

For several Claude Code runs, all test cases were executed inside a single bash call. That means:

- `llm_overhead_s` is near zero by construction
- wall time mostly equals tool execution time
- its overhead numbers are not directly comparable to agents that executed each case as separate steps

This affects at least:

- `social-account-analyzer`
- `viral-trend-finder`
- `social-posting`
- `long-to-short-video` (batched into two large bash sessions)

### 2. Managed Claude Agent often used parallel dispatch but sequential execution

`managed-claude-agent` frequently dispatched multiple tool calls at once, but the container executed them sequentially. So its logs look parallel at the orchestration layer, while actual compute remained serialized.

### 3. Some skill inputs drifted across platforms

The biggest example is `viral-trend-finder`:

- `claudecode` analyzed a **60s / 12.2MB** video in T3
- `pikabot` analyzed a **15s / 1.0MB** TikTok video in T3
- `managed-claude-agent` analyzed a **165-frame Instagram reel** with a **38.2MB** CDN fallback path
- `codex` analyzed a different Instagram asset again

So `viral-trend-finder` wall times are directionally useful, but not fully strict head-to-head timings.

### 4. Long-to-short-video had retries and non-determinism

`long-to-short-video` includes:

- intermittent Apify / signed URL issues on Claude Code
- one `pikabot` T1 SIGTERM and cache-backed rerun
- non-deterministic clip count in T4 (`3`, `4`, or `4` clips depending on run)

So this skill is still comparable, but results should be read as **real-world operational performance**, not a deterministic microbenchmark.

---

## Headline Results

### Wall-clock winner per skill

| Skill | Fastest platform | Wall time | Slowest platform | Wall time | Spread |
|------|------------------|-----------|------------------|-----------|--------|
| social-account-analyzer | `pikabot` | 286.6s | `claudecode` | 379.9s | 1.33x |
| viral-trend-finder | `claudecode` | 359.0s | `codex` | 480.4s | 1.34x |
| social-posting | `claudecode` | 107.1s | `codex` | 188.4s | 1.76x |
| long-to-short-video | `managed-claude-agent` | 824.3s | `pikabot` | 1923.6s | 2.33x |

### Cheapest platform per skill

| Skill | Cheapest platform | Cost |
|------|-------------------|------|
| social-account-analyzer | `managed-claude-agent` | $0.1347 |
| viral-trend-finder | `managed-claude-agent` | $0.1194 |
| social-posting | `managed-claude-agent` | $0.0624 |
| long-to-short-video | `managed-claude-agent` | $0.2459 |

### Time Comparison Matrix (wall time, seconds)

| Skill | pikabot | managed-claude-agent | claudecode | codex | Fastest |
|------|---------|----------------------|------------|-------|---------|
| social-account-analyzer | **286.6** | 355.3 | 379.9 | 316.8 | `pikabot` |
| viral-trend-finder | 384.0 | 447.4 | **359.0** | 480.4 | `claudecode` |
| social-posting | 137.3 | 149.7 | **107.1** | 188.4 | `claudecode` |
| long-to-short-video | 1923.6 | **824.3** | 1124.4 | 1325.5 | `managed-claude-agent` |

### Tool Execution Time Matrix (`tool_calls_s`)

| Skill | pikabot | managed-claude-agent | claudecode | codex |
|------|---------|----------------------|------------|-------|
| social-account-analyzer | 239.8 | 312.2 | 379.9 | 265.7 |
| viral-trend-finder | 314.8 | 388.4 | 358.9 | 341.0 |
| social-posting | 68.4 | 117.8 | 107.0 | 77.8 |
| long-to-short-video | 1449.9 | 701.7 | 1124.3 | 1114.4 |

### Orchestration / Overhead Time Matrix (`llm_overhead_s`)

| Skill | pikabot | managed-claude-agent | claudecode | codex |
|------|---------|----------------------|------------|-------|
| social-account-analyzer | 46.8 | 43.1 | 0.0* | 51.1 |
| viral-trend-finder | 69.1 | 59.0 | 0.2* | 139.5 |
| social-posting | 68.9 | 31.9 | 0.1* | 110.6 |
| long-to-short-video | 473.7 | 122.6 | 0.0* | 211.1 |

`*` Claude Code overhead is artificially compressed by single-bash batching and should not be read as true zero-cost orchestration.

### Agent Aggregate Time Totals (all 4 skills combined)

| Platform | Total wall time | Total tool time | Total overhead | Average `llm_pct` |
|----------|-----------------|-----------------|----------------|-------------------|
| `pikabot` | 2731.5s | 2072.8s | 658.6s | 27.3% |
| `managed-claude-agent` | **1776.7s** | **1520.1s** | **256.6s** | 15.4% |
| `claudecode` | 1970.4s | 1970.0s | 0.3s* | 0.04%* |
| `codex` | 2311.2s | 1799.0s | 512.3s | 29.9% |

### Fastest / Slowest Spread by Skill

| Skill | Fastest | Slowest | Spread |
|------|---------|---------|--------|
| social-account-analyzer | `pikabot` 286.6s | `claudecode` 379.9s | 1.33x |
| viral-trend-finder | `claudecode` 359.0s | `codex` 480.4s | 1.34x |
| social-posting | `claudecode` 107.1s | `codex` 188.4s | 1.76x |
| long-to-short-video | `managed-claude-agent` 824.3s | `pikabot` 1923.6s | 2.33x |

### Median wall time by platform

| Platform | Median wall time | Average `llm_pct` | Total cost across 4 skills |
|----------|------------------|-------------------|-----------------------------|
| `pikabot` | 335.3s | 27.3% | $4.4257 |
| `claudecode` | 369.4s | 0.04%* | $2.1540 |
| `managed-claude-agent` | 401.4s | 15.4% | $0.5624 |
| `codex` | 398.6s | 29.9% | $28.1659 |

`*` Claude Code's average `llm_pct` is not directly comparable because several runs were measured as single bash sessions.

---

## Skill-By-Skill Analysis

## 1. social-account-analyzer

### Ranking

| Platform | Wall | Tool calls | Overhead | Cost |
|----------|------|------------|----------|------|
| `pikabot` | **286.6s** | 239.8s | 46.8s | $0.2649 |
| `codex` | 316.8s | 265.7s | 51.1s | $4.7939 |
| `managed-claude-agent` | 355.3s | 312.2s | 43.1s | **$0.1347** |
| `claudecode` | 379.9s | 379.9s | ~0s* | $0.2118 |

### What matters

- This skill is dominated by **in-script LLM time**, not orchestration. Every platform saw roughly fixed two-pass analysis cost per account.
- The recurring bug is consistent across agents: **pass-2 JSON truncation followed by repair**.
- The main source of variance is fetch latency:
  - Instagram public scraping is slowest
  - X/RapidAPI is fastest
  - TikTok sits in the middle

### Takeaway

`pikabot` is the strongest wall-clock runtime here. That likely means its execution path, network path to third-party APIs, and general environment are favorable for this specific skill. But the margin over `codex` is only about **30s**, so this is not a blowout.

The more important insight is that **all 4 platforms are bottlenecked by the skill's own two-pass LLM design**, not by orchestration. This skill needs product/skill fixes more than agent fixes:

- reduce pass-2 truncation
- reduce output volume
- trim prompt size or split response contracts

---

## 2. viral-trend-finder

### Ranking

| Platform | Wall | Tool calls | Overhead | Cost |
|----------|------|------------|----------|------|
| `claudecode` | **359.0s** | 358.9s | ~0s* | $0.4263 |
| `pikabot` | 384.0s | 314.8s | 69.1s | $0.9085 |
| `managed-claude-agent` | 447.4s | 388.4s | 59.0s | **$0.1194** |
| `codex` | 480.4s | 341.0s | 139.5s | $11.1569 |

### What matters

This skill has the worst cross-platform comparability in the set.

- T3 assets differed materially across platforms.
- T3 often hit **Anthropic timeout / retry / OpenAI fallback**.
- T4 frequently hit **TikTok trending fallback** paths.
- MCA had an init race on T1.

The important stable pattern is not the exact ranking. It is this:

- **T3 dominates total wall time** on every platform
- the dominant bottleneck is usually **LLM synthesis**, not frame extraction
- the skill is operationally resilient because it keeps succeeding through fallback chains

### Takeaway

`claudecode` has the best raw wall time in the recorded runs, but this is not a clean “Claude Code is faster” conclusion because:

- its orchestration overhead is compressed to near zero
- its T3 asset differs from other runs

A safer summary is:

- `pikabot` and `claudecode` are in the same rough band for this skill
- `managed-claude-agent` is slower but cheapest
- `codex` is clearly the least efficient option here, especially on cost

This skill's main issue is not agent choice. It is **fallback-heavy behavior and unstable upstream LLM synthesis latency**.

---

## 3. social-posting

### Ranking

| Platform | Wall | Tool calls | Overhead | Cost |
|----------|------|------------|----------|------|
| `claudecode` | **107.1s** | 107.0s | ~0s* | $0.4727 |
| `pikabot` | 137.3s | 68.4s | 68.9s | $0.3597 |
| `managed-claude-agent` | 149.7s | 117.8s | 31.9s | **$0.0624** |
| `codex` | 188.4s | 77.8s | 110.6s | $7.8308 |

### What matters

This is the cleanest pure-LLM skill in the set, and one bug is universal:

- `T4 --variations 3` failed everywhere or degraded everywhere
- common failure mode: **Anthropic timeout or malformed/truncated JSON array**, then fallback to a single caption

That makes `social-posting` useful because it separates two things clearly:

- the skill's own generation latency
- the agent/runtime orchestration overhead

### Takeaway

This is the skill where `codex` looks worst.

- `tool_calls_s` is not especially high
- but `llm_overhead_s` is huge: **110.6s**, or **58.7%** of wall time
- that is far above `managed-claude-agent` and above `pikabot`

So for short, mostly text-generation workflows, `codex` is a poor runtime from a cost/performance perspective in this batch.

For practical deployment:

- `claudecode` is fastest by wall time
- `managed-claude-agent` is by far the cheapest
- `pikabot` is competitive on wall time but burns a lot of overhead relative to actual script runtime

---

## 4. long-to-short-video

### Ranking

| Platform | Wall | Tool calls | Overhead | Cost |
|----------|------|------------|----------|------|
| `managed-claude-agent` | **824.3s** | 701.7s | 122.6s | **$0.2459** |
| `claudecode` | 1124.4s | 1124.3s | ~0s* | $1.0432 |
| `codex` | 1325.5s | 1114.4s | 211.1s | $4.3843 |
| `pikabot` | 1923.6s | 1449.9s | 473.7s | $2.8926 |

### What matters

This is the most operationally revealing skill in the dataset.

Common behavior across platforms:

- T2 cache hits are extremely fast everywhere
- S1 Apify is fairly consistent across platforms
- S3 clip selection is relatively cheap
- the true bottleneck is **S4-S7 per-clip media processing**

Important differences:

- `managed-claude-agent` was dramatically faster than `pikabot`
- `claudecode` also beat `pikabot` comfortably
- `pikabot` suffered a kill/rerun and was slowest by a large margin
- T4 returned fewer clips than requested on every platform, but the exact count varied (`3` vs `4`), showing model/runtime non-determinism

### Takeaway

This is the skill where the hierarchy is clearest:

1. `managed-claude-agent`
2. `claudecode`
3. `codex`
4. `pikabot`

The likely explanation is not LLM orchestration. It is **media pipeline execution efficiency**:

- ffmpeg/OpenCV throughput
- container CPU characteristics
- background execution/polling pattern
- fewer costly restarts and retries

This is the strongest evidence in the batch that heavy video pipelines should not default to `pikabot` if wall time matters.

---

## Cross-Skill Platform Assessment

## PikaBot

### Strengths

- Fastest on `social-account-analyzer`
- Competitive on `viral-trend-finder`
- Competitive on `social-posting`
- Good caching behavior
- Reasonable costs compared with Codex

### Weaknesses

- Long-video pipeline performance is poor in this batch
- Overhead remains significant on every skill
- Susceptible to operational issues like T1 SIGTERM on `long-to-short-video`

### Bottom line

`pikabot` is still viable for light-to-medium skill execution, especially where its network path or in-cluster integrations help. But it is not the best general-purpose runtime in this set.

## Managed Claude Agent

### Strengths

- Cheapest on all 4 skills
- Best result on the heaviest skill (`long-to-short-video`)
- Moderate overhead profile
- Good operational strategies for long tasks (`nohup`, polling, retries)

### Weaknesses

- Sequential execution under parallel dispatch wastes some orchestration intent
- Init-script races and container-startup complexity can create reliability problems
- Not always fastest on lighter skills

### Bottom line

`managed-claude-agent` is the strongest overall platform in this batch if you optimize for **cost discipline + good heavy-work performance + acceptable orchestration overhead**.

## Claude Code

### Strengths

- Fastest wall time on `viral-trend-finder` and `social-posting`
- Strong result on `long-to-short-video`
- Low apparent orchestration overhead in these measurements

### Weaknesses

- `llm_overhead_s` is artificially minimized by batched shell execution, so the metric is not directly comparable
- Some runs required reruns or had intermittent actor/download issues
- Not cheapest

### Bottom line

`claudecode` looks strong in raw wall-clock terms, but this dataset over-favors it on orchestration metrics. It is clearly good, but not as decisively dominant as the raw tables might suggest.

## Codex

### Strengths

- Consistently completes all skills
- Competitive but not leading on `social-account-analyzer`
- Respectable result on `long-to-short-video` compared with `pikabot`

### Weaknesses

- Most expensive platform on every skill
- Never fastest
- Particularly poor overhead profile on `social-posting` and `viral-trend-finder`

### Bottom line

In this dataset, `codex` is the least attractive benchmark platform for these skills. It works, but it pays too much in both tokens and wall-clock overhead to justify itself against the Claude-based alternatives.

---

## Repeated Failure Patterns Across Skills

These issues appear across multiple platforms and skills, so they should be treated as **skill-level problems**, not just agent-level problems.

### 1. Anthropic proxy instability

Observed in:

- `social-account-analyzer`
- `viral-trend-finder`
- `social-posting`

Symptoms:

- ReadTimeout
- malformed/truncated JSON
- OpenAI fallback paths
- higher latency spikes in long prompts or synthesis steps

### 2. Variation / multi-item generation instability

Observed in:

- `social-posting` T4 (`--variations 3`)
- `long-to-short-video` T4 (requested clip count not achieved)

Symptoms:

- requested N outputs, got fewer than N
- fallback to single result
- non-deterministic boundaries on viable candidates

### 3. Cache systems are working well

Observed in:

- `long-to-short-video` T2 on every platform
- `managed-claude-agent` and `pikabot` reuse flows

This is the healthiest part of the stack. When cache hits happen, the speedups are dramatic.

---

## Final Judgment

If I had to summarize the 16 runs in one sentence:

**`managed-claude-agent` is the best all-around runtime, `claudecode` has the best raw wall times but benefits from friendlier measurement methodology, `pikabot` is competitive on lighter skills but weakest on heavy video, and `codex` is consistently the most expensive and never the clear best choice.`**

More concretely:

- Choose **`managed-claude-agent`** when you want the best overall balance of speed, price, and long-running workflow handling.
- Choose **`claudecode`** when raw local execution speed matters and you're comfortable treating its overhead measurements as non-comparable.
- Choose **`pikabot`** for lighter integrated skill runs where its environment advantages help, but do not expect it to lead on long media pipelines.
- Do **not** choose **`codex`** as the default benchmark winner for this skill family based on this dataset.

---

## Recommended Next Step

For the next round, the single most valuable improvement would be to standardize methodology across all 4 platforms:

1. run each test case as a separate timed step
2. avoid single-bash batching on Claude Code
3. lock the exact T3 input asset for `viral-trend-finder`
4. lock retry accounting rules for `long-to-short-video`
5. report both orchestration overhead and in-skill LLM/API time separately

That would turn this comparison from **directionally strong** into **strictly decision-grade**.
