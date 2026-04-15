# Benchmark Report — short-film / managed-claude-agent / Opus 4.6 / Run 1

**Platform:** managed-claude-agent  
**Date:** 2026-04-15  
**Session total:** 72m 4s (4324s) · active: 64m 4s (3844s) · idle (user confirmations): 8m (480s)  
**Prompt:** The Hargrove Library — gothic horror, 12 shots, 60s, portrait 9:16, sfx_hint path  
**Output:** 60.26s · 1080×1920 · H.264+AAC · 43.6 MB  
**CDN URL:** https://cdn.pika.art/v2/files/agent/eb064606-0e26-4d56-97ae-3c543c14ce41/final.mp4 ✅  
**Session:** `sesn_011Ca5ER8bNLzhcLU24rcWWi`  
**Agent:** `agent_011Ca5DzAVnAckNg438cPSR1` (v1)  
**Env:** `env_01C7HCQETarSF2XMLwzx2PGZ`  

---

## Phase Breakdown

| Phase | Start (UTC) | End (UTC) | Duration | Notes |
|-------|-------------|-----------|----------|-------|
| Session boot + env setup | 08:21:25 | 08:25:22 | 237s | Container provisioned, GitHub resource mounted, env vars exported |
| Stage 0+1: Init + Plan | 08:25:22 | 08:25:44 | 22s | Project dir created, 12-shot story plan written (226ms compute) |
| Stage 2: Assets (Gemini) | 08:26:00 | 08:27:22 | 82s | 5 images (2 characters + 3 scenes). 30% Gemini 503 rate, retried missing 3 in 25s |
| **Stage 2.5: Script review (idle)** | 08:27:30 | 08:31:11 | 221s | User confirmation wait (~3m 40s) — auto-confirmed via monitor_mca.py |
| Stage 3: Keyframes (Gemini) | 08:31:11 | 08:37:28 | 377s | 12 shots, 9:16 portrait. First pass 295s (tmux timeout, shots 05+12 failed 504). Retry 29s. PIL grids manually recomposed. |
| **Stage 3.5: Keyframe review (idle)** | 08:37:35 | 08:38:31 | 56s | User confirmation wait (~56s) — auto-confirmed via monitor_mca.py |
| Stage 3.6: Music (MiniMax) | 08:38:47 | 08:44:32 | 46.8s | Parallel with Stage 4. 26s score, 815KB. |
| Stage 4: Video (Kling) — submit | 08:38:47 | 08:38:54 | ~15s | 5 batches submitted (resubmitted 2× due to crashes) |
| Stage 4: Kling render + crash loop | 08:38:54 | 09:20:35 | 2501s | B1/B3/B4/B5 done in 5-7 min; **B2 took 37 min**. 4 container crashes during polling/recovery: crash at 08:50:51, 09:03:17, 09:13:34, 09:15:42. Each crash = ~8-10 min container restart. |
| Stage 4: Download + normalize + concat | 09:26:32 | 09:27:57 | ~85s | 5 clips downloaded (Kling CDN 503s required retries), normalized to 1080×1920, concatenated. |
| Stage 4.5: Lipsync (sfx_hint path) | 09:28:13 | 09:28:14 | 0.5s | Music overlay only (no TTS/fal). Already completed during earlier crash-recovery turn. |
| Agent final report + CDN confirm | 09:28:15 | 09:29:09 | 54s | Agent compiled timing report and confirmed CDN URL |
| **Total (session)** | **08:21:25** | **09:29:09** | **4324s / 72m 4s** | Session created to status_idle |

---

## Container Crash Timeline

The container crashed 4 times during Stage 4 (video pipeline), each requiring ~8-10 min recovery:

| # | Time (UTC) | Context | Recovery |
|---|-----------|---------|----------|
| 1 | 08:50:51 | During video.py second run (Kling poll loop, 295s timeout) | Container restarted at ~09:00:49 (10 min). Agent read project.json + output/ state |
| 2 | 09:03:17 | During `cat project.json \| python3` diagnostic | Container restarted at ~09:08:18 (5 min). tmux timeout on `ls` |
| 3 | 09:13:34 | During manual resume script (full download+normalize+concat) | Agent retried with minimal Kling status check |
| 4 | 09:15:42 | During second full resume attempt | Agent issued minimal B2-only poll script |

**Root cause uncertain** — all crashes occurred during heavy Python execution (requests + subprocess + ThreadPoolExecutor). Lighter scripts (simple status checks) reliably succeeded. Possible OOM or process count limit.

---

## Token Usage

| Token type | Count |
|------------|-------|
| input_tokens | 892 |
| output_tokens | 30,976 |
| cache_read_tokens | 1,948,742 |
| cache_write_tokens | 202,966 |
| effective_input_tokens | 2,152,600 |
| total_tokens | 2,183,576 |

**Estimated cost: $9.07** (Opus 4.6: $15/$75/$18.75/$1.50 per million)

Cache write (202,966) is 5× higher than music-video run2 (42,660) — reflects more turns and longer tool results due to 4 crash-recovery loops. Cache read (1,948,742) similarly elevated.

---

## Key Findings

1. **video.py lacks resume from _omni_jobs_state.json** — When video.py is re-run (e.g. after container crash), it re-submits all 5 Kling batches instead of resuming from saved job IDs. This caused 3 separate Kling batch submission rounds. The agent worked around this by manually reading the state file and polling job IDs directly.  
   **Fix:** Add `--resume` flag to video.py that reads `_omni_jobs_state.json` job IDs, polls their status, and downloads completed clips without re-submitting.

2. **Container crashes on concurrent Python workloads** — All 4 crashes occurred during scripts that used `ThreadPoolExecutor` or `subprocess` concurrently (downloading 5 clips in parallel, running ffmpeg, etc.). Lightweight single-threaded scripts reliably completed. Likely OOM or process/fd limit in container.  
   **Fix:** Reduce concurrency in download/normalize step; add per-operation memory bounds (e.g. sequential download instead of parallel, or smaller thread pool).

3. **Kling B2 batch outlier** — B2 (shots 04-06) took ~37 min vs 5-7 min for B1/B3/B4/B5. All batches were submitted simultaneously. No error — B2 eventually succeeded. Likely Kling queue/resource contention for that batch.

4. **Gemini flakiness ~30%** — 3 of 5 asset images and 2 of 12 keyframe shots failed on first pass (503/504). The pipeline handled this gracefully: assets.py and keyframes.py both detect partial completion and retry only missing items.

5. **Stage 3.6 (music) fully parallel** — MiniMax music completed in 46.8s while Kling was still rendering. No net wall-time cost for music generation.

6. **sfx_hint path = instant lipsync** — With no dialogue shots (sfx_hint-only), Stage 4.5 is a simple audio overlay (0.5s). This is the recommended path for benchmarking speed.

7. **High cost for run1** — $9.07 vs $3.45 for music-video run2. The 4 crash-recovery loops each added ~15-20 LLM turns with large context, tripling the cache write and read tokens.

---

## Recommendations

1. **Add `--resume` to video.py** — Read `_omni_jobs_state.json`, skip already-completed batches, poll in-progress jobs. This would eliminate re-submission on crash and cut Stage 4 time significantly on unstable containers.

2. **Sequential download in Stage 4** — Replace `ThreadPoolExecutor` download with sequential loop to reduce memory/fd pressure in the container. Download time adds only ~5-10s per clip.

3. **Smaller bash scripts, more turns** — Monolithic scripts (full pipeline in one tmux) crash the container. Splitting into smaller steps (submit → poll → download → normalize → concat as separate tool calls) would make recovery trivial and avoid the 295s tmux timeout entirely.

4. **Pre-export PYTHONPATH in environment** — The agent currently adds `export PYTHONPATH=...` to every script block. Setting this in the environment config would simplify agent prompts and reduce error surface.

5. **Stage 4 batching smoke test** — Run a quick 1-shot Kling test at session start to detect if the environment supports concurrent subprocess/requests workloads before running the full 5-batch pipeline.
