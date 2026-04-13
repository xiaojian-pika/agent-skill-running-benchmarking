# Video-Translation E2E Comparison — Round 2 (post-fix)

**Date:** 2026-04-09
**Video:** charli-daily-vlog.mp4 (720x1280, 67.8s)
**Target:** es (Spanish), no lip sync

## Wall Clock Summary

| | PikaBot (EKS pod) | Claude Code (devbox) |
|--|-------------------|---------------------|
| Tool calls total | 55.0s | 50.3s |
| LLM overhead | ~638.2s | ~27.0s |
| **WALL TOTAL** | **693.2s (11m33s)** | **77.3s (1m17s)** |
| | | **Claude Code 9.0x faster e2e** |

## Per-Phase Comparison

### Phase 1 — Install

| Step | PikaBot | Claude Code |
|------|---------|-------------|
| cms_fetch | 0.55s | N/A |
| skill_install | 0.13s | N/A |
| subagent_session_start | ~1s | N/A |

### Phase 2 — Download

| Step | PikaBot | Claude Code |
|------|---------|-------------|
| download_video | 0.40s | 0.39s |

### Phase 3 — Skill Execution

| Step | PikaBot | Claude Code | Delta |
|------|---------|-------------|-------|
| probe_video | 0.08s | 0.01s | ~Same |
| skill_run total | 30.59s | 49.91s | **PikaBot 1.6x faster** |
| — extract_audio | 0.90s | 1.60s | PikaBot 1.8x |
| — whisper_transcribe (API) | 2.30s | 4.30s | PikaBot 1.9x |
| — translate_gpt4o (API) | 1.80s | 4.80s | PikaBot 2.7x |
| — voice_clone (API) | 2.00s | 5.60s | PikaBot 2.8x |
| — tts_eleven_v3 (API) | 21.70s | 29.20s | PikaBot 1.3x |
| — replace_audio (ffmpeg) | 1.89s | 4.40s | PikaBot 2.3x |

### Phase 4 — Delivery

| Step | PikaBot | Claude Code |
|------|---------|-------------|
| upload_output | 22.25s | 0s (local) |

### LLM Overhead

| | PikaBot | Claude Code |
|--|---------|-------------|
| LLM thinking total | **~638.2s** | ~27.0s |
| % of wall time | **92%** | 35% |

## Analysis

### 638s LLM overhead — the worst across all skills

PikaBot's subagent took ~507s between being spawned and starting the skill run. This dwarfs everything else. The actual skill work (30.6s) is only **4.4% of wall time**.

```
PikaBot wall time breakdown:
  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Skill: 55s (8%)
  ██████████████████████████████░░  LLM: 638s (92%)
```

### Skill execution is close

Tool calls are nearly identical: PikaBot 55s vs Claude Code 50.3s. PikaBot is slightly faster on API calls (in-cluster proxy) and ffmpeg (better CPU), but Claude Code's upload-free delivery evens it out.

### API calls: PikaBot has consistent proxy advantage

Every API call is 1.3-2.8x faster on PikaBot — in-cluster proxy vs external Cloudflare URL. But this saves only ~15s total, negligible against 638s of LLM overhead.

### TTS remains the skill-level bottleneck

| | PikaBot | Claude Code |
|--|---------|-------------|
| TTS time | 21.7s (71% of skill) | 29.2s (58% of skill) |

ElevenLabs TTS dominates skill execution on both platforms.

## Round 1 vs Round 2

### PikaBot

| Metric | Round 1 | Round 2 | Change |
|--------|---------|---------|--------|
| skill_run | 29.2s | 30.6s | ~Same |
| upload | ~3s | 22.3s | Worse (CDN variance) |
| LLM overhead | ~60-80s (est.) | 638.2s | **8-10x worse** |
| WALL TOTAL | ~105s (est.) | 693.2s | **6.6x slower** |

Round 1 had auth issues so LLM overhead wasn't cleanly measured, but this round's 638s is clearly an outlier — the subagent startup ate ~507s.

### Claude Code

| Metric | Round 1 | Round 2 | Change |
|--------|---------|---------|--------|
| skill_run | 41.3s | 49.9s | ~Same (API variance) |
| LLM overhead | 19.0s | 27.0s | ~Same |
| WALL TOTAL | 60.7s | 77.3s | ~Same |

## Raw Logs

### PikaBot

```
PHASE 1: cms_fetch 0.55s, install 0.13s, subagent ~1s
PHASE 2: download 0.40s
PHASE 3: probe 0.08s, skill_run 30.59s
  extract_audio 0.90s, whisper 2.30s, translate 1.80s
  voice_clone 2.00s, tts 21.70s, replace_audio 1.89s
PHASE 4: upload 22.25s
LLM_OVERHEAD: ~638.2s
WALL_TOTAL: 693.2s
Output size: 3220 KB
```

### Claude Code

```
PHASE 2: download 0.39s
PHASE 3: probe 0.01s, skill_run 49.91s
  extract_audio 1.6s, whisper 4.3s, translate 4.8s
  voice_clone 5.6s, tts 29.2s, replace_audio 4.4s
LLM_OVERHEAD: ~27.0s
WALL_TOTAL: 77.3s
Output size: 3368 KB
```
