# Benchmark Report: social-posting — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** T1 X casual, T2 Instagram casual, T3 TikTok funny, T4 Instagram ×3 variations
**Content brief:** "video tutorial: how to cook perfect pasta at home — tested 5 different techniques"
**Cost:** $0.4727 (input $3/M + output $15/M + cache_read $0.3/M + cache_write $3.75/M)
**Result:** PARTIAL — T1/T2/T3 SUCCESS, T4 DEGRADED (1 variation returned instead of 3)

## Timing Summary

| Step | Duration | llm_s | Notes |
|------|----------|-------|-------|
| T1 — X casual | **6.748s** | 6.6s | caption 172 chars, 2 hashtags |
| T2 — Instagram casual | **18.075s** | 18.0s | caption 990 chars, 30 hashtags |
| T3 — TikTok funny | **7.302s** | 7.2s | caption 76 chars, 4 hashtags |
| T4 — Instagram ×3 variations | **74.849s** | ~74.8s (3 calls) | 1 variation returned (degraded) |
| **Total tool calls** | **106.974s** | | |
| **CC LLM overhead** | **0.134s** | | single bash call, measurement noise |
| **Wall total** | **107.108s** | | |

- CC LLM overhead: **~0%** (single bash call)
- Skill execution: **~100%** of wall time
- Internal LLM breakdown: T1/T3 ~7s each (short outputs), T2 ~18s (long IG caption), T4 ~75s (degraded 3-call chain)

## Results per Test Case

### T1 — X/Twitter (casual)
- **Output:** caption=172 chars, hashtags=['#pasta','#cooking'], full_post=188 chars
- **Style:** Contrarian take ("salting the water matters less than you think") within 280-char limit
- **LLM:** 6.6s via Anthropic

### T2 — Instagram (casual)
- **Output:** caption=990 chars, 30 hashtags
- **Style:** APP formula — opener "I was wrong about cooking pasta until I actually tested 5 different techniques"
- **LLM:** 18.0s via Anthropic — longer call matches longer output (30 hashtags + full APP-format caption)

### T3 — TikTok (funny)
- **Output:** caption=76 chars ("I tested 5 pasta techniques so you don't have to (your nonna lied to you fr)"), 4 hashtags
- **Style:** Short hook format (<100 chars), Gen-Z register, 4 hashtags including #fyp
- **LLM:** 7.2s via Anthropic

### T4 — Instagram ×3 variations (DEGRADED)
- **Expected:** 3 variation objects as JSON array
- **Returned:** 1 variation (single caption, 910 chars, 30 hashtags)
- **Failure chain:** Anthropic ReadTimeout (30.1s) → OpenAI fallback (28.7s, returned invalid JSON array `[]`) → skill caught error → fell back to `generate_single_caption()` via Anthropic (16.0s) → returned 1 result
- **Note:** Skill version f8353cf fixes `--variations N` max_tokens scaling (truncation bug), but the timeout-triggered fallback chain still collapses to single result. Root cause is Anthropic proxy instability on the longer variations prompt, not token truncation.

## Observations

- **T4 variations failure is proxy-driven, not a token issue:** The latest fix (f8353cf) addresses max_tokens scaling for variations, but when Anthropic proxy times out entirely (30s ReadTimeout), the OpenAI fallback receives the full prompt and returns an empty/malformed array. The skill then silently returns 1 result. This is consistent with the Anthropic proxy instability seen in VTF and SAA benchmarks.

- **Output quality gap T1 vs T2/T3:** T1 (X) caption is 172 chars — well-formed, fits the 280-char limit, contrarian tone. T3 (TikTok) at 76 chars is tight and on-format. T2 (Instagram) at 990 chars with 30 hashtags matches platform expectations.

- **LLM time scales with output length:** T1~6.6s (short), T3~7.2s (short), T2~18.0s (long IG), linear with expected output size. This is the expected pattern for a pure-LLM skill with no external API calls.

- **Skill is fastest among benchmarked skills:** Wall total 107s for 4 calls. Compare VTF (359s) and SAA (380s) which include external API fetches. Social-posting is purely LLM-bound.
