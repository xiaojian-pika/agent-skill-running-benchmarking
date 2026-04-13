# Benchmark Report: social-posting on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** T1 X/Twitter casual, T2 Instagram casual, T3 TikTok funny, T4 Instagram ×3 variations
**Session:** sesn_011CZvH19AFxaV9wfs36K1ry

## Results

| Metric | Value |
|--------|-------|
| Wall total | **149.7s** |
| Tool execution (parallel-adjusted) | 117.8s (78.7%) |
| LLM overhead | 31.9s (21.3%) |
| Tokens (total) | 19,020 |
| Estimated cost | $0.062 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Initial LLM (read task + dispatch) | — | 17.0s | 17.0s |
| T1+T2+T3+T4 parallel dispatch (sequential container) | 117.8s | — | 117.8s |
| Final LLM (results synthesis) | — | 14.9s | 14.9s |

## Per-Script Timing

| Test | Script total | LLM (in-script) | Backend | Result | Notes |
|------|-------------|-----------------|---------|--------|-------|
| T1 X casual | 9.1s | 8.9s | Anthropic | ✅ caption_len=216 hashtags=2 | Compact, under 280 chars |
| T2 Instagram casual | 17.8s | 17.6s | Anthropic | ✅ caption_len=1005 hashtags=28 | Full long-form micro-story |
| T3 TikTok funny | 7.2s | 7.0s | Anthropic | ✅ caption_len=86 | Short Gen-Z hook |
| T4 Instagram ×3 vars | 79.2s | 14.4s | OpenAI fallback | ⚠️ 1 variation (expected 3) | Anthropic timed out (31.7s) |

## T4 Failure Chain (stderr)

```
⚠️ Anthropic failed after 31.7s (The read operation timed out), trying OpenAI fallback...
⚠️ Variations generation failed (The read operation timed out). Returning single result.
⚠️ Anthropic failed after 2.5s (Remote end closed connection without response), trying OpenAI fallback...
⏱️ [llm] 14.4s  (openai)
```

**Root cause:** `--variations 3` on Instagram triggers a large token budget (max_tokens=1700). Anthropic call timed out at 31.7s. Fallback to OpenAI also hit the variations failure path and returned single variation. Second attempt (for single caption) also failed on Anthropic → OpenAI fallback succeeded in 14.4s.

## Key Observations

- **Parallel dispatch, sequential container execution:** Agent dispatched T1+T2+T3+T4 simultaneously (14:50:48Z). Container ran them sequentially (T1→T2→T3→T4). All results returned at 14:52:45-46Z. Parallel-adjusted wall = 117.8s; sequential sum = 113.2s (+4.6s container overhead).

- **T3 is the fastest (7.2s):** TikTok captions are the shortest (≤150 chars), fewest hashtags — smallest token budget → fastest LLM call.

- **T2 is the slowest successful test (17.8s):** Instagram long-form captions generate 1000+ chars + 28 hashtags = large output → longer LLM call.

- **T4 regression — variations timeout (known issue):** `--variations 3` uses `max_tokens = max(1200, n×500+200) = 1700`. On MCA, Anthropic read timeouts fire at ~31.7s, which hits before the full 3-variation JSON is returned. v1.0.7 includes a dynamic `max_tokens` fix but the timeout threshold in the MCA environment is stricter than PikaBot/Claude Code. PikaBot (T4=28s LLM + fallback, still got 1 variation), Codex (T4 likely similar). Only 1 variation returned from OpenAI fallback.

- **llm_pct = 21.3%:** Higher than VTF (13.2%) and SAA orchestration-only (12.1%), because social-posting script LLM calls are short (7-18s) with relatively more orchestration overhead (17s dispatch + 15s synthesis). Unlike SAA, there's no additional in-script LLM beyond what's visible in tool_calls_s — all 4 `⏱️ [llm]` values are inside bash tool calls.

- **Cost: $0.062** — cheapest MCA benchmark so far. Low input token count (4 uncached) and small output (2446 tokens). Cache miss on write (6014 tokens) — this is the first run, system prompt not cached. Second run would be significantly cheaper (cache_read dominates).

- **LLM backend breakdown:** T1/T2/T3 → Anthropic; T4 → OpenAI fallback. The 3 successful Anthropic calls took 8.9+17.6+7.0 = 33.5s total script-level LLM time. T4's OpenAI call took 14.4s (including timeout retries = 31.7+2.5+14.4 = 48.6s wall for T4's LLM activity).

- **Skill installed via init_script embed:** social-posting is not on the Pika hub. `generate_caption.py` (18.6KB) and `_retry.py` (2.4KB) were base64-encoded inline in pika-sp-env's init_script. nova3-common (skill_01WVFxRuNsjXYwW9Tz7Q2Nks) provides `nova3_common.config` which is imported by the skill.
