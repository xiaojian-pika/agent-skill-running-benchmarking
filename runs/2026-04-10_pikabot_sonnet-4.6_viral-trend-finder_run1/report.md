# viral-trend-finder Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** viral-trend-finder 1.0.6

## Results

| Metric | Value |
|--------|-------|
| Wall total | **384.0s** |
| Tool calls | 314.8s (82.0%) |
| LLM overhead | 69.1s (18.0%) |
| Total tokens | 1,012,510 |
| Estimated cost | $0.9085 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.121s |
| skill_install | 0s (pre-installed) |
| T1 find fitness (TikTok+IG) | 20.7s |
| T2 find cooking (X) | 2.0s |
| T3 analyze (@pandafitness7) | 220.7s |
| T4 trending (general) | 69.0s |
| upload_result | 2.3s |

## Per-test results

| Test | Duration | Results | Notes |
|------|----------|---------|-------|
| T1 find fitness (TikTok+IG) | 20.7s | 10 results | 5 TikTok + 5 Instagram, top 239.6K views |
| T2 find cooking (X) | 2.0s | 9 results | RapidAPI fast, top 798K views |
| T3 analyze (TikTok URL) | 220.7s | 7 shots / 15 frames | ⚠️ Anthropic proxy timeout → OpenAI fallback |
| T4 trending (general) | 69.0s | 10 results | TikTok native trending=0, fell back to 15 keyword searches |

## T3 sub-stages (inferred from stderr)

| Stage | Est. Time |
|-------|-----------|
| metadata fetch | ~2s |
| video download (1010KB) | ~5s |
| frame extract (15 frames) | ~3s |
| Gemini Vision (15 frames) | ~130s |
| LLM synthesis (w/ OpenAI fallback) | ~80s |

## Token breakdown

| Type | Tokens |
|------|--------|
| input_tokens | 7 |
| output_tokens | 3,316 |
| cache_read_tokens | 848,024 |
| cache_write_tokens | 161,163 |
| **total** | **1,012,510** |

## Observations

- **T3 dominates**: 220.7s = 70.6% of all skill execution time. Gemini Vision (15 frames) + LLM synthesis = bottleneck.
- **T2 is fastest**: 2.0s — RapidAPI X is very fast.
- **T1 moderate**: 20.7s — Apify TikTok + Instagram parallel fetch.
- **T4 slow due to fallback**: TikTok native trending returned 0 → 15 keyword searches × 3 platforms = 69s.
- **Anthropic proxy timeout on T3**: LLM synthesis hit ReadTimeout (2 retries), fell back to OpenAI. T3 still succeeded.
- **Cache efficiency**: 83.7% cache reads — system prompt + context well-cached.
- CDN: https://cdn.pika.art/v2/files/agent/e405b9cf-2f03-4f6e-a3ac-5e686caee152/bench_vtf_run1_result.json
