# social-posting Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** social-posting 1.0.7

## Results

| Metric | Value |
|--------|-------|
| Wall total | **137.3s** |
| Tool calls | 68.4s (49.8%) |
| LLM overhead | 68.9s (50.2%) |
| Total tokens | 999,630 |
| Estimated cost | $0.3597 |

## Timing breakdown

| Step | Time | LLM (stderr) |
|------|------|--------------|
| cms_fetch | 0.125s | — |
| T1 X casual | 4.6s | 4.5s |
| T2 Instagram casual | 14.5s | 14.5s |
| T3 TikTok funny | 4.5s | 4.5s |
| T4 Instagram ×3 variations | 42.6s | 28.0s + 14.5s (2 passes) |
| upload_result | 2.0s | — |

## Per-test results

| Test | Duration | Output | Notes |
|------|----------|--------|-------|
| T1 X casual | 4.6s | caption=177chars, hashtags=2 | ✅ Clean |
| T2 Instagram casual | 14.5s | caption=846chars, hashtags=27 | ✅ Clean, long-form |
| T3 TikTok funny | 4.5s | caption=78chars, hashtags=4 | ✅ Clean, short hook |
| T4 Instagram ×3 variations | 42.6s | variations_returned=1 (expected 3) | ⚠️ Truncation fallback |

## Observations

- **T4 variations bug still present in v1.0.7**: First LLM pass (28s) returned truncated JSON array — fell back to single-variation second pass (14.5s). Total 42.5s for 1 variation.
- **LLM time scales with output length**: X=4.5s, TikTok=4.5s, Instagram=14.5s — long-form captions (846 chars + 27 hashtags) take 3× longer.
- **Agent overhead balanced**: llm_overhead=68.9s ≈ tool_calls=68.4s (50/50 split).
- **Token efficiency**: 99.3% cache reads — very cheap per run ($0.36 total).
- CDN: https://cdn.pika.art/v2/files/agent/e36ca8cf-13fc-48d7-9329-ff6b1a477806/bench_sp_run1_result.json
