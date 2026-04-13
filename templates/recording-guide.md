# Benchmark Recording Guide

How to fill in `benchmark-run.json` after running a test.

## meta — Basic info

| Field | How to get it |
|-------|---------------|
| `date` | Test date, format `YYYY-MM-DD` |
| `round` | Which round of testing (1, 2, 3...) |
| `tester` | Your name |
| `notes` | Anything special about this run |
| `test_input` | Describe the input file (video name, resolution, duration, codec, size, URL) |

## task — What you're testing

| Field | How to get it |
|-------|---------------|
| `name` | Skill name or test scenario, e.g. `video-translation` |
| `version` | Skill version (from CMS or git) |
| `purpose` | What you're testing and why, e.g. "Translate 67s short video to Spanish, no lip sync" |
| `expected_output` | What a successful run produces, e.g. "A Spanish-dubbed mp4 video file" |

## platform — Where you ran it

| Field | How to get it |
|-------|---------------|
| `name` | `pikabot` / `claudecode` / `managed-claude-agent` / `codex` |
| `runtime` | `EKS pod` / `staging devbox` / `local Mac` / etc. |
| `llm_model` | e.g. `Claude Opus 4.6`, `Claude Sonnet 4.6` |
| `system_prompt_tokens` | PikaBot: check pod logs for prompt size. Claude Code: check session stats. Fill `null` if unknown |

## phases — Timing per stage

Each phase has:
- Tool execution times (the actual commands/API calls)
- `llm_overhead_s` — LLM thinking time during this phase
- `total_s` — phase wall clock total
- `tokens` — input/output tokens consumed in this phase (fill `null` if not separable)

### install
- `cms_fetch_s` — Time to fetch skill bundle URL from CMS
- `skill_install_s` — Time to download zip + extract
- `subagent_start_s` — Time for subagent session to boot
- Skip entirely (set all to `null`) if skill was pre-installed or not applicable (e.g. Claude Code)

### asset_acquisition
- `download_s` — Time to download test input files

### execution
- `probe_s` — Time to probe/analyze input file (e.g. ffprobe)
- `skill_run_s` — Total skill script wall time
- `steps[]` — Individual sub-steps within the skill run. Add as many as the skill has. Fill `duration_s: null` if not individually timed
- Common step names: `extract_audio`, `whisper_transcribe`, `translate_gpt4o`, `voice_clone`, `tts_eleven_v3`, `replace_audio`

### delivery
- `upload_s` — Upload time. `0` if local delivery
- `output_size_kb` — Output file size in KB
- `output_url` — CDN URL if uploaded, empty string if local

## tokens — Total token usage

| Field | How to get it |
|-------|---------------|
| `input_tokens` | Claude Code: shown in session summary. PikaBot: sum from pod API logs |
| `output_tokens` | Same as above |
| `cache_read_tokens` | Claude Code: shown in session stats. Fill `null` if not applicable |
| `cache_write_tokens` | Same as above |
| `total_tokens` | Use the **platform-reported authoritative value** (from API response, session stats, or extractor tool). Do NOT manually sum the components — use the value the platform reports. |

**Platform differences in token counting:**
- **Claude (PikaBot, Claude Code, MCA):** `cache_read_tokens` and `cache_write_tokens` are **separate from** `input_tokens`. Total = input + output + cache_read + cache_write.
- **OpenAI (Codex):** `cached_input_tokens` is a **subset of** `input_tokens` (already counted within it). Total = input + output. Cache tokens are informational only — do not add them to input.

**Note on cost calculation:** Cost is always derived from the component fields × their respective prices, NOT from `total_tokens`. For Claude: `input×price + output×price + cache_read×cr_price + cache_write×cw_price`. For OpenAI: `(input - cached)×full_price + cached×discounted_price + output×price`.

## cost — Estimated cost

| Field | How to get it |
|-------|---------------|
| `model` | Same as `platform.llm_model` |
| `input_price_per_million` | Check Anthropic/OpenAI pricing page for the model |
| `output_price_per_million` | Same |
| `cache_read_price_per_million` | Cache read price (e.g. $0.30/M for Sonnet 4.6). Set to `null` if model has no caching |
| `cache_write_price_per_million` | Cache write price (e.g. $3.75/M for Sonnet 4.6). Set to `null` if model has no caching |
| `estimated_cost_usd` | Platform-specific formula (see below) |

**Cost formulas by platform:**
- **Claude (PikaBot, Claude Code, MCA):** `(input × input_price + output × output_price + cache_read × cache_read_price + cache_write × cache_write_price) / 1,000,000` — all token fields are additive.
- **OpenAI (Codex):** `((input - cache_read) × input_price + cache_read × cache_read_price + output × output_price) / 1,000,000` — cache_read is a **subset** of input, not additive. If `cache_read_price` is not declared, use simple: `(input × input_price + output × output_price) / 1,000,000`.

Current pricing reference (2026-04):

| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| Claude Opus 4.6 | $15/M | $75/M | $18.75/M | $1.50/M |
| Claude Sonnet 4.6 | $3/M | $15/M | $3.75/M | $0.30/M |
| GPT-5.4 / GPT-5-Codex | $2.50/M | $10/M | — | — |

**Note on Claude caching:** With prompt caching, most input tokens appear in `cache_read_tokens`, not `input_tokens`. The real input cost = `input_tokens × input_price + cache_read × cache_read_price + cache_write × cache_write_price`.

## totals — Summary

| Field | How to get it |
|-------|---------------|
| `tool_calls_s` | Sum of all tool/compute time across phases |
| `llm_overhead_s` | Total LLM thinking time (wall_total - tool_calls) |
| `wall_total_s` | End-to-end wall clock time |
| `llm_pct` | `llm_overhead_s / wall_total_s × 100` |
| `skill_pct` | `tool_calls_s / wall_total_s × 100` |
