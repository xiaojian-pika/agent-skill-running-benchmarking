# social-account-analyzer Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** social-account-analyzer 1.0.8

## Results

| Metric | Value |
|--------|-------|
| Wall total | **286.6s** |
| Tool calls | 239.8s (83.7%) |
| LLM overhead | 46.8s (16.3%) |
| Total tokens | 683,182 |
| Estimated cost | $0.2649 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.117s |
| skill_install | 0s (pre-installed) |
| T1 Instagram @natgeo | 96.9s |
| T2 X @NASA | 63.9s |
| T3 TikTok @khaby.lame | 76.8s |
| upload_result | 2.1s |

## Per-account results

| Account | Platform | Followers | Eng Rate | fetch_s | llm_s | Exit |
|---------|----------|-----------|----------|---------|-------|------|
| @natgeo | Instagram | 274,960,938 | 0.03% | 31.7s | 65.0s | 0 |
| @NASA | X/Twitter | 90,943,693 | 0.03% | 1.5s | 62.2s | 0 |
| @khaby.lame | TikTok | 160,600,000 | 0.90% | 6.4s | 70.2s | 0 |

## Token breakdown

| Type | Tokens |
|------|--------|
| input_tokens | 6 |
| output_tokens | 3,184 |
| cache_read_tokens | 676,178 |
| cache_write_tokens | 3,814 |
| **total** | **683,182** |

Cache read ratio: 99.0% — system prompt + prior context almost entirely cached.

## Observations

- All 3 accounts succeeded (exit=0). No data gaps.
- **LLM overhead 46.8s (16.3%)** — agent thinking time between tool calls.
- **LLM truncation auto-repair** triggered on pass 2 for all 3 — repair succeeded each time.
- **Skill LLM dominates execution time**: ~62-70s per account (2-pass Anthropic analysis), consistent across platforms.
- **Fetch time varies by platform**: Instagram (Apify, 31.7s) >> TikTok (Apify, 6.4s) >> X (RapidAPI, 1.5s).
- **Token efficiency**: 99% cache reads — very cheap per run ($0.26 total).
- CDN: https://cdn.pika.art/v2/files/agent/21f2b9ad-1132-47cd-acde-43592672faf8/bench_saa_round1_result_v2.json
