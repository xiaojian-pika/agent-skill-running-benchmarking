# Benchmark Report — music-video / managed-claude-agent / Opus 4.6 / Run 1

**Platform:** managed-claude-agent  
**Date:** 2026-04-13  
**Wall time:** ~73.9 min (4432s) — includes ~12 min stream-disconnect tail  
**Song:** APT. — ROSÉ & Bruno Mars (30s Apple Music preview)  
**Engine:** Kling via `kling_via_fal` (direct API 429) + LTX-2.3 lipsync  
**Output:** 11 clips, ~30s, 1080×1920 — delivered to CDN (URL not captured, see below)  
**Session:** `sesn_011Ca1jsqx8LZH4NdmpJ3R6m`  
**Agent:** `agent_011Ca1fKcqjAaSUVrwXruTgE` (v2)  
**Env:** `env_01C7HCQETarSF2XMLwzx2PGZ`  

---

## Phase Breakdown (estimates — stream dropped at keyframe gen; rest from session stats)

| Phase | Wall time | Notes |
|-------|-----------|-------|
| Env setup + container boot | 50s | Agent booted, exported env vars |
| Python env setup (PYTHONPATH) | 57s | pip install failed, manual PYTHONPATH export |
| Apple Music + ffmpeg | 83s | 2 DNS failures, proxy call, direct download |
| Shot script gen (LLM) | 25s | 11 clips |
| Batch creation | 8s | 3 batches of 4/4/3 |
| Character ref gen (Gemini) | 27s | 1.4MB PNG |
| Keyframe gen (Gemini × 11) | ~180s | Stream dropped here; timing estimated |
| **Parallel video gen (3 workers × 11 clips)** | **~1000s** | Background subprocesses, agent polls every 60s |
| Assembly (normalize+concat+mix) | ~30s | 11 clips |
| Captions (Whisper + ffmpeg) | ~60s | faster-whisper CPU |
| CDN upload | ~15s | URL not captured |
| Background worker wait (idle) | ~2679s | Workers run in bash; container "idle" during this time |

---

## Cross-Platform Comparison (Kling engine, APT. 30s)

| Metric | claudecode run2 (Kling) | MCA run1 (Kling) | Δ |
|--------|------------------------|-----------------|---|
| Wall total | **977s** | **4432s** | +354% |
| Active compute | 925s (tool_calls_s) | 1753s (active_seconds) | +90% |
| Clips | 9 | 11 | +2 clips |
| Parallel workers | 3 LLM subagents | 3 headless subprocesses | different |
| Worker timeout issue | W1 timed out (~571s) | None (subprocesses, no stream) | MCA better |
| LLM model | Sonnet 4.6 | Opus 4.6 | different |
| Output tokens | 29,388 | 13,855 | -53% |
| Cache read tokens | 2,583,487 | 1,219,315 | -53% |
| Cost | $2.05 | $3.20 | +56% |

**Note:** MCA wall time is inflated by ~720s (12 min) due to stream-disconnect tail after session completed.  
Adjusted MCA estimate: **~3710s (61.8 min)**.

---

## Token Usage

| Token type | Count |
|------------|-------|
| input_tokens | 301 |
| output_tokens | 13,855 |
| cache_read_tokens | 1,219,315 |
| cache_write_tokens | 17,435 |
| effective_input_tokens | 1,237,051 |
| total_tokens | 1,250,906 |

Workers are headless subprocesses — only the coordinator agent (Opus 4.6) generates tokens.  
Fewer output tokens vs Claude Code (13.8K vs 29.4K): workers don't stream progress to the LLM.  
**Estimated cost: $3.197** (Opus 4.6: $15/75/$18.75/$1.50 per million)

---

## Key Findings

1. **SSE stream not suitable for long sessions** — `RemoteProtocolError: incomplete chunked read` after ~5-10 min. Session ran to completion in background. For MCA sessions > 15 min, must use polling (`--no-stream`) not streaming.

2. **Events API 100-event cap** — `/v1/sessions/{id}/events` returns first 100 events only. For long sessions (11+ clips, ~74 min), the final delivery message (CDN URL) is beyond event 100. CDN URL not captured in this run.

3. **Beta header split** — `/v1/sessions/stream` requires `agent-api-2026-03-01`, all other endpoints use `managed-agents-2026-04-01`. Fixed in `run_session.py` mid-run.

4. **nova3_common not on PYTHONPATH** — Container has the skills repo mounted but `nova3_common` isn't auto-added to PYTHONPATH. `pip install -e .` fails (wheel build error). Workaround: manual `PYTHONPATH=/workspace/nova3-agent-skills:$PYTHONPATH`. Should be fixed in env config.

5. **Apple Music DNS failures** — `[Errno -3] Temporary failure in name resolution` on first 2 direct DNS calls. Agent debugged and used proxy API successfully on 3rd attempt. Adds ~60-80s overhead.

6. **Subprocess workers = no stream timeout** — Claude Code workers (LLM subagents) hit stream idle timeout at ~571s on run2 (Kling FAL ~225s/clip × 3 clips). MCA workers are bash subprocesses — no timeout issue. This is a real MCA advantage for long-running clip generators.

7. **Opus 4.6 vs Sonnet 4.6** — Using Opus 4.6 for the coordinator. Higher cost ($3.20 vs $2.05) but fewer output tokens (13.8K vs 29.4K). Opus 4.6 produces more concise reasoning.

## Recommendations

- **Fix PYTHONPATH in environment config**: Add `ENV PYTHONPATH=/workspace/nova3-agent-skills` or install via pip properly
- **Use `--no-stream` for production**: SSE drops for sessions > 10 min  
- **Increase events API limit or add pagination**: 100-event cap is insufficient for 70+ min sessions
- **Add DNS retry in apple_music.py**: Script should retry on DNS failure rather than failing immediately
- **CDN URL logging**: Worker should write CDN URL to a file (e.g., `/tmp/music-video/result.txt`) as backup in case event API misses it
