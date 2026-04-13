# Benchmark Report: social-account-analyzer — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** Analyze @natgeo (Instagram), @NASA (X/Twitter), @khaby.lame (TikTok)
**Result:** SUCCESS — all 3 accounts analyzed

## Timing Summary

| Step | Fetch | LLM (pass1+2) | Total |
|------|-------|---------------|-------|
| T1 — @natgeo Instagram | 42.9s | 83.7s | **126.7s** |
| T2 — @NASA X/Twitter | 5.8s | 158.7s | **164.7s** |
| T3 — @khaby.lame TikTok | 17.8s | 70.5s | **88.5s** |
| **Total tool calls** | **66.5s** | **312.9s** | **379.9s** |
| **CC LLM overhead** | | | **0.014s** |
| **Wall total** | | | **379.866s** |

- CC LLM overhead: **~0%** (single bash call, no inter-run CC activity)
- Skill execution: **~100%** of wall time
- Internal LLM proxy calls (Anthropic pass1+pass2): **82.4%** of tool time
- Fetch: **17.5%** of tool time

## Results per Account

### T1 — @natgeo (Instagram)
- **Followers:** 274,960,878 | **Avg ER:** 0.03% | **Best type:** Carousel | **Trend:** stable

### T2 — @NASA (X/Twitter)
- **Followers:** 90,943,570 | **Avg ER:** 0.03% | **Best type:** Video | **Trend:** growing

### T3 — @khaby.lame (TikTok)
- **Followers:** 160,600,000 | **Avg ER:** 0.9% | **Best type:** Video | **Trend:** declining

## Observations

- **T2 LLM spike (158.7s):** Anthropic proxy latency was unusually high during the @NASA analysis. Fetch time (5.8s) was normal, confirming the spike is in the proxy layer, not the data fetch.

- **LLM JSON truncation on all 3 runs:** Auto-repair succeeded each time. The two-pass output consistently exceeds max_tokens and relies on `_repair_truncated_json()`. Increasing pass1 `max_tokens` from 2800 would address this.

- **Apify fetch variance:** Instagram fetch (42.9s) was slow due to Apify cold start. X/Twitter via RapidAPI (5.8s) and TikTok via Apify (17.8s) are within normal range.

- **CC overhead ~0:** `llm_overhead_s = 0.014s` is measurement noise from running T1/T2/T3 in a single continuous bash call. Skill-pct ≈ 100%.
