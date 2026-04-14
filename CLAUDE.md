# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Standardized framework for benchmarking agent skill performance across platforms (PikaBot, Claude Code, Managed Claude Agent, Codex). Tracks per-phase timing, token usage, and estimated cost in a unified JSON format.

## Directory Structure

```
testing-samples/     — Benchmark prompts per skill (each has PikaBot/CC/MCA/Codex sections)
templates/           — JSON template + recording guide
runs/                — All benchmark results (one directory per run)
reports/             — Cross-platform comparison reports
archive/             — Legacy markdown files from early testing
tools/               — Validation + token extraction scripts
```

## Workflow: Submitting a Benchmark Run

1. Pick a skill prompt from `testing-samples/benchmark-prompt-<skill>.md`
2. Follow the platform-specific section (PikaBot, Claude Code, Managed Agent, or Codex)
3. Each run gets a directory: `runs/YYYY-MM-DD_platform_model_skill-name_runN`
   - Platform: `pikabot` / `claudecode` / `managed-claude-agent` / `codex`
   - Use `_` between segments, `-` within segment names
4. Each run must have `result.json` (from template) + `report.md`
5. Validate: `python3 tools/validate-run.py runs/<dir>/`
6. Commit and push

## JSON Format

Seven sections: `meta`, `task`, `platform`, `phases`, `tokens`, `cost`, `totals`.
Phases: **install → asset_acquisition → execution → delivery**.
See `templates/recording-guide.md` for field-by-field instructions.

## Token Extraction Tools

### Claude Code
```bash
python3 tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
- `--after`/`--before` isolate tokens to a single task within a session
- Claude API caching note: most input tokens appear in `cache_read_tokens`, not `input_tokens`. Use `effective_input_tokens` (= input + cache_read + cache_write) for real input cost

### Codex
```bash
python3 tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
- `--after`/`--before` compute delta between cumulative `token_count` snapshots
- Without flags: returns final cumulative total (entire session — wrong if multiple tasks ran)

### PikaBot
Parse session JSONL at `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter `type="message"`, `role="assistant"` entries within the benchmark timestamp window. Sum `message.usage.{input, output, cacheRead, cacheWrite}`.

### Managed Claude Agent
Token data comes from session metadata API: `GET /v1/sessions/{id}` → `usage` field.

## Validation

```bash
python3 tools/validate-run.py runs/<dir>/
```
Checks: required fields, timing sanity (wall >= tool, wall >= llm), token sums, report.md exists.

## Pricing Reference (2026-04)

| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| Claude Opus 4.6 | $15/M | $75/M | $18.75/M | $1.50/M |
| Claude Sonnet 4.6 | $3/M | $15/M | $3.75/M | $0.30/M |
| GPT-5.4 / GPT-5-Codex | $2.50/M | $10/M | — | — |

## Test Assets

Standard test video: `charli-daily-vlog.mp4` (720x1280, 67.8s, HEVC+AAC, 4.9MB)
URL: `https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4`

## Skills Benchmarked

| Skill | Type | Key API deps |
|-------|------|-------------|
| video-captions | CPU-heavy (whisper + ffmpeg) | None (fully local) |
| music-beat-sync | Mixed (MiniMax API + ffmpeg) | PIKA proxy → MiniMax |
| video-translation | API-heavy (Whisper + GPT-4o + ElevenLabs) | PIKA proxy → multiple |
| apple-music | Pure API | PIKA proxy → Apple Music |
| long-to-short-video | CPU-heavy | PIKA proxy |
| social-account-analyzer | API-heavy | PIKA proxy → social APIs |
| social-posting | API-heavy | PIKA proxy → Composio |
| viral-trend-finder | API-heavy | PIKA proxy → social APIs |
| short-film | API-heavy (multi-stage generative) | PIKA proxy → Gemini + Kling + MiniMax + fal |

## Key Findings (April 2026)

- LLM overhead accounts for 18-92% of wall time depending on platform and skill
- PikaBot's 106K system prompt is the primary overhead driver
- CDN upload adds 2-150s variance (PikaBot only)
- No single platform wins all skills — Codex fastest for simple tasks, Claude Code for complex ones
- For sub-second skills (apple-music), agent orchestration overhead is the only thing that matters
