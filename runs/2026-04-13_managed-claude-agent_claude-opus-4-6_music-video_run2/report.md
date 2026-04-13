# Benchmark Report — music-video / managed-claude-agent / Opus 4.6 / Run 2

**Platform:** managed-claude-agent  
**Date:** 2026-04-13  
**Wall time:** 27.6 min (1653s) — no stream-disconnect tail  
**Song:** APT. — ROSÉ & Bruno Mars (30s Apple Music preview)  
**Engine:** Kling via `kling_via_fal` (direct API 429)  
**Output:** 10 clips, ~30s, 1080×1920 — delivered to CDN ✅  
**CDN URL:** https://cdn.pika.art/v2/files/agent/ad7cdde8-1cbb-4b99-88c2-cc998840ab38/final.mp4  
**Session:** `sesn_011Ca1szHXMmXX6G7EEER1oM`  
**Agent:** `agent_011Ca1fKcqjAaSUVrwXruTgE` (v3)  
**Env:** `env_01C7HCQETarSF2XMLwzx2PGZ`  

---

## Phase Breakdown

| Phase | Start (UTC) | End (UTC) | Duration | Notes |
|-------|-------------|-----------|----------|-------|
| Env setup + boot | 13:51:45 | 13:52:27 | 42s | Agent booted, env vars exported |
| Apple Music + ffmpeg | 13:52:32 | 13:53:48 | 76s | Proxy call successful (no DNS failures this run) |
| Shot script gen | 13:53:48 | 13:54:36 | 48s | 10 clips for 29.99s audio |
| Batch creation | 13:54:17 | 13:54:25 | 8s | 3 batches (4+4+2) |
| Character ref gen | 13:54:36 | 13:55:51 | 75s | Gemini text-to-image, 1387KB JPG |
| **Keyframe gen** | 13:55:55 | 14:03:09 | **434s** | CLI invocation (slow — see findings) |
| Worker spawn | 14:03:09 | 14:03:24 | 15s | 3 background subprocesses |
| Container crash+recover | — | 14:04:52 | — | Workers survived, no clips lost |
| **Parallel video gen** | 14:03:24 | 14:10:53 | **449s** | 10 clips via FAL Kling (~90s/clip) |
| Assembly | 14:10:59 | 14:11:45 | 46s | normalize + concat + audio mix |
| **Captions + CDN + cleanup** | 14:11:45 | 14:17:57 | **372s** | faster-whisper first-run download |
| **Total** | 13:51:45 | 14:17:57 | **1572s** | session.status_idle event |

---

## Cross-Platform Comparison (Kling engine, APT. 30s)

| Metric | CC run2 (Kling) | MCA run1 (Kling) | MCA run2 (Kling) | Δ (MCA r2 vs r1) |
|--------|----------------|-----------------|-----------------|------------------|
| Wall total | **977s** | 4432s | **1653s** | **−63%** |
| Wall total (min) | 16.3 min | 73.9 min | 27.6 min | −63% |
| Active compute | 925s | 1754s | 1565s | −11% |
| Clips | 9 | 11 | 10 | −1 |
| Keyframe time | — | ~180s | 434s | +141% |
| Clip gen time | — | ~1000s | 449s | −55% |
| Captions time | — | ~60s | ~361s | +502% |
| Stream tail waste | 0s | ~720s+ | **0s** | fixed |
| CDN URL captured | ✅ | ❌ | ✅ | fixed |
| Output tokens | 29,388 | 13,855 | 13,109 | −5% |
| Cache read tokens | 2,583,487 | 1,219,315 | 1,111,282 | −9% |
| Cost | $2.05 | $3.20 | **$3.45** | +8% |

**MCA run2 vs run1 improvement: 4432s → 1653s (−63% wall time)**  
Primary gain: eliminated 12-min stream-disconnect tail. Secondary: faster clip generation (~90s/clip vs ~225s/clip via FAL).

---

## Token Usage

| Token type | Count |
|------------|-------|
| input_tokens | 215 |
| output_tokens | 13,109 |
| cache_read_tokens | 1,111,282 |
| cache_write_tokens | 42,660 |
| effective_input_tokens | 1,154,157 |
| total_tokens | 1,167,266 |

Workers are headless subprocesses — only the coordinator agent generates tokens.  
**Estimated cost: $3.453** (Opus 4.6: $15/75/$18.75/$1.50 per million)

---

## Key Findings

1. **Stream reconnect `?after=` not supported** — `/v1/sessions/{id}/stream?after=` returns `400: Failed to unmarshal request`. The cursor-based reconnect logic added in run2 doesn't work. The local observer (run_session.py) stopped writing to jsonl after event 100 (first stream close). Session ran to completion correctly in the container. CDN URL recovered via events API polling.  
   **Fix:** On reconnect, open stream without `?after=` cursor. Server sends new events from current position. OR fall back to polling events REST API which DOES support `?after=`.

2. **CDN URL now captured** — result.txt backup write (added in run2 system prompt) + events API polling successfully retrieved the URL. This resolves run1's main gap.

3. **Stream-disconnect tail eliminated** — run1's ~12 min tail (SSE drop + no reconnect) is gone. run2 wall = 1653s vs run1's ~3710s adjusted estimate.

4. **Container crash at 14:04:52** — Container crashed 82s after worker spawn (during monitoring sleep). Session resumed immediately. Workers survived as bash background processes. 3 clips were already done when the agent recovered.

5. **Keyframe CLI vs Python import** — run2 agent used `python3 keyframes.py --project-dir` (CLI) instead of `from keyframes import generate_keyframes` (Python import). Result: 434s for 10 clips vs ~180s in run1 for 11 clips. CLI initialization + likely different code path.  
   **Fix:** Enforce Python import pattern in system prompt; forbid CLI invocation.

6. **Captions first-run download** — Captions took ~361s vs ~60s in run1. Likely faster-whisper model download on first run in a fresh container. One-time overhead.  
   **Fix:** Pre-download faster-whisper model in environment image.

7. **Clip generation faster** — FAL Kling throughput improved: ~90s/clip in run2 vs ~225s/clip in run1. Both used `kling_via_fal` (direct API 429 in both runs). This may reflect FAL infrastructure improvement or lower load.

## Recommendations

- **Fix stream reconnect**: Drop `?after=` from stream URL on reconnect. Server delivers new events from session's current position without needing a cursor.
- **Enforce keyframe Python import**: Change system prompt Step 5b to disallow CLI invocation of keyframes.py — it's much slower.
- **Pre-install faster-whisper model**: Add `RUN python3 -c "from faster_whisper import WhisperModel; WhisperModel('small')"` to environment Dockerfile to avoid first-run download.
- **Fix PYTHONPATH**: Add `PYTHONPATH=/workspace/nova3-agent-skills` to environment config (same as run1 recommendation — still not fixed).
