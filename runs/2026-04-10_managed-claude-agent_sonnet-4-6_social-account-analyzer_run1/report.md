# Benchmark Report: social-account-analyzer on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** Analyze @natgeo (Instagram), @NASA (X/Twitter), @khaby.lame (TikTok)
**Session:** sesn_011CZv5PBenrtU3Pi5ta79ry

## Results

| Metric | Value |
|--------|-------|
| Wall total | **355.3s** |
| Tool execution (non-overlapping) | 312.2s (88%) |
| LLM overhead (orchestration only) | 43.1s (12%) |
| True LLM (orchestration + in-script) | **270.6s (76.2%)** |
| Tokens (total) | 52,530 |
| Estimated cost | $0.135 |

> **Note on LLM%:** `llm_overhead_s` (43.1s) captures only inter-tool orchestration LLM time. The skill itself runs 2 LLM passes per account (~75s each × 3 = 227.5s total) inside the bash tool calls. True LLM time = 43.1 + 227.5 = **270.6s = 76.2% of wall** — consistent with other MCA skills.

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Read SKILL.md | 3.1s | 14.3s | 17.4s |
| T1+T2+T3 (parallel dispatch, sequential in container) | 307s | 6.3s | 313.3s |
| Cat / read results | 2.1s | 18.5s | 20.6s |

## Per-Script Timing

| Test | Script total | Fetch | LLM (in-script) | Result |
|------|-------------|-------|-----------------|--------|
| T1 @natgeo (Instagram) | 124.5s | 49.1s | 74.9s | ✅ success |
| T2 @NASA (X/Twitter) | 83.0s | 6.7s | 76.0s | ✅ success |
| T3 @khaby.lame (TikTok) | 96.5s | 19.6s | 76.6s | ✅ success |

## Analysis Output Summary

| Account | Platform | Followers | ER | Avg Likes | Avg Views | Freq/week | Best Format | Trend |
|---------|----------|-----------|----|-----------|-----------|-----------|-------------|-------|
| @natgeo | Instagram | 274.9M | 0.03% | 71K | 321K | 3.8× | Carousel | insufficient_data |
| @NASA | X/Twitter | 90.9M | 0.03% | 26.6K | 727K | 20× | Video | Growing |
| @khaby.lame | TikTok | 160.7M | 0.91% | 1.44M | 30.17M | 1× | Video | Growing |

## Key Observations

- **Root cause of run1 failure confirmed:** The agent system prompt hardcoded a stale `PIKA_AGENT_API_KEY` (`ak_cQfKGajtqfJnOEs...`) that lacked Apify/RapidAPI access. Using the correct key (`ak_z2rUc3OO...` from `~/keys/.env`) fixed all 3 test cases.

- **True LLM% is 76.2%, not 12.1%** — SAA is unique among benchmarked skills in running internal LLM calls (2-pass analysis via Pika proxy, ~75s/account). This time is inside the bash tool calls and not visible to the orchestrator's `llm_overhead_s`. When included, LLM dominance is consistent with all other MCA skills (75–80%).

- **Parallel tool dispatch, sequential container execution:** The agent issued T1, T2, T3 bash calls simultaneously (same event timestamp 12:18:20Z). The container ran them sequentially: T1=124.5s + T2=83.0s + T3=96.5s = 304s, returned all results at once at 12:23:27Z.

- **LLM JSON truncation on all 3 pass-2 calls** — `⚠️ LLM JSON truncated, attempting repair...` triggered for every account. Auto-repair succeeded in all cases. Known issue in v1.0.7. Adds latency but does not fail the analysis.

- **Fetch times vary 7× by platform:**
  - X/Twitter (RapidAPI): **6.7s** — fastest, no cold-start
  - TikTok (Apify): **19.6s**
  - Instagram (Apify): **49.1s** — slowest; own Connect Proxy attempted first (failed), then Apify public scraper with cold-start overhead

- **In-script LLM is platform-agnostic:** 74.9s / 76.0s / 76.6s across Instagram, X, TikTok — essentially a fixed ~75s cost per account regardless of platform. Fetch is where platforms diverge.

- **Cost: $0.135** — session token cost only (orchestration LLM). In-script LLM (~227s × 3 accounts) routes through Pika proxy and is not counted in session usage.
