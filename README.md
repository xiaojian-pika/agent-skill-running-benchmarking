# Agent Skill Benchmarking

> **Repo:** [Mellis-Labs/agent-skill-running-benchmarking](https://github.com/Mellis-Labs/agent-skill-running-benchmarking) (private)
> **Team:** Nova 3 / Agent Skills
> **Maintainer:** Jiajun

Standardized framework for benchmarking agent skill performance across platforms.

## What This Repo Does

- Provides a unified JSON format for recording skill benchmark results
- Tracks per-phase timing (install → asset acquisition → execution → delivery), token usage, and estimated cost
- Makes it easy to compare the same skill across different platforms (PikaBot, Claude Code, Managed Claude Agent, Codex)
- Includes token extraction tools for Claude Code and Codex sessions
- Anyone can run a benchmark and submit results by following the steps below

## Directory Structure

```
testing-samples/     — Benchmark prompts per skill (PikaBot / CC / MCA / Codex sections)
templates/           — JSON template + recording guide
runs/                — All benchmark results (one directory per run)
reports/             — Cross-platform comparison reports
archive/             — Legacy markdown files from early testing
tools/               — Validation + token extraction scripts
```

## Skills Benchmarked

| Skill | Type | Prompt file |
|-------|------|-------------|
| video-captions | CPU-heavy (whisper + ffmpeg) | `benchmark-prompt-video-captions.md` |
| music-beat-sync | Mixed (MiniMax API + ffmpeg) | `benchmark-prompt-music-beat-sync.md` |
| video-translation | API-heavy (Whisper + GPT-4o + ElevenLabs) | `benchmark-prompt-video-translation.md` |
| apple-music | Pure API | `benchmark-prompt-apple-music.md` |
| long-to-short-video | CPU-heavy | `benchmark-prompt-long-to-short-video.md` |
| social-account-analyzer | API-heavy | `benchmark-prompt-social-account-analyzer.md` |
| social-posting | API-heavy | `benchmark-prompt-social-posting.md` |
| viral-trend-finder | API-heavy | `benchmark-prompt-viral-trend-finder.md` |

## How to Submit a Benchmark Run

### 1. Pick a skill and platform

Each prompt file in `testing-samples/` has sections for all 4 platforms:
- **PikaBot** — installs from CMS, uploads to CDN, token tracking via session JSONL parsing
- **Claude Code** — runs skill from local repo, no upload, token tracking via `tools/extract-cc-tokens.py`
- **Managed Claude Agent** — orchestrated via Anthropic Sessions API, token tracking from session metadata
- **Codex** — runs skill from local repo, no upload, token tracking via `tools/extract-codex-tokens.py`

### 2. Create a run directory

```bash
mkdir runs/YYYY-MM-DD_platform_model_skill-name_runN
```

Naming convention: `{date}_{platform}_{model}_{test-target}_{run-number}`
- Date: `YYYY-MM-DD`
- Platform: `pikabot` / `claudecode` / `managed-claude-agent` / `codex`
- Model: `sonnet-4.6` / `opus-4.6` / `gpt-5-4` etc.
- Run number: `run1`, `run2`, `run3`...
- Use `_` to separate segments, `-` within segment names

Example: `2026-04-10_pikabot_sonnet-4.6_video-captions_run1`

### 3. Fill in result.json

Copy `templates/benchmark-run.json` into your run directory as `result.json`. Fill in all fields — see `templates/recording-guide.md` for field-by-field instructions.

### 4. Write report.md

Create a `report.md` in the same directory. Can be brief or detailed — the JSON is the source of truth, the report is for humans.

### 5. Validate

```bash
python3 tools/validate-run.py runs/your-run-directory/
```

Must pass with zero errors. Warnings for missing tokens/cost are acceptable but fill them if you can.

### 6. Commit & Push

```bash
git add runs/your-run-directory/
git commit -m "Add benchmark: YYYY-MM-DD platform model skill-name runN"
git push
```

## Token Extraction Tools

### Claude Code

```bash
python3 tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

Use `--after`/`--before` to isolate tokens to a single benchmark task. Without these flags, the tool sums the entire session.

**Note:** With Claude caching, most input tokens appear in `cache_read_tokens`, not `input_tokens`. The `effective_input_tokens` field gives the real total.

### Codex

```bash
python3 tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

Computes delta between cumulative `token_count` snapshots. Without `--after`/`--before`, returns the final cumulative total (wrong if multiple tasks ran in the session).

### PikaBot

Parse session JSONL at `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter `type="message"`, `role="assistant"` entries within the benchmark timestamp window. Sum `message.usage.{input, output, cacheRead, cacheWrite}`.

### Managed Claude Agent

Token data comes from session metadata: `GET /v1/sessions/{id}` → `usage` field.

## Platforms

| Platform | Runtime | Description |
|----------|---------|-------------|
| `pikabot` | EKS pod | PikaBot agent with 106K system prompt, CDN upload |
| `claudecode` | Devbox / local Mac | Claude Code CLI, local skill execution |
| `managed-claude-agent` | Anthropic container | Managed agent via Sessions API |
| `codex` | Codex sandbox | OpenAI Codex CLI |

## JSON Format Overview

Each run captures:

| Section | What it records |
|---------|----------------|
| **meta** | Date, round, tester, test input file info |
| **task** | Skill name, version, test purpose, expected output |
| **platform** | Platform name, runtime environment, LLM model |
| **phases** | Per-stage timing: install → asset acquisition → execution → delivery |
| **tokens** | Input/output/cache token counts (total + per-phase) |
| **cost** | Model pricing + estimated USD cost |
| **totals** | Wall clock, tool time, LLM overhead, percentages |

## Pricing Reference (2026-04)

| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| Claude Opus 4.6 | $15/M | $75/M | $18.75/M | $1.50/M |
| Claude Sonnet 4.6 | $3/M | $15/M | $3.75/M | $0.30/M |
| GPT-5.4 / GPT-5-Codex | $2.50/M | $10/M | — | — |

## Key Metrics We Track

- **Wall clock time** — end-to-end duration from start to finish
- **LLM overhead** — time the model spends thinking between tool calls
- **Skill execution time** — actual tool/script running time
- **Token usage** — input, output, cache read/write tokens per phase and total
- **Estimated cost** — USD cost based on model pricing × token usage
- **Upload/delivery variance** — time to deliver output (CDN upload vs local)

## Background

Early benchmarking (April 2026) found that LLM overhead accounts for 18-92% of wall time depending on platform and skill, while skill execution itself is often fast. No single platform wins all skills — Codex is fastest for simple tasks, Claude Code for complex ones. PikaBot's 106K system prompt is the primary overhead driver. Raw logs from early rounds are preserved in `archive/`. This repo standardizes the recording format so we can track improvements over time.
