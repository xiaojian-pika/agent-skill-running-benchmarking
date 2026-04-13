# music-beat-sync Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** music-beat-sync 1.0.6

## Results

| Metric | Value |
|--------|-------|
| Wall total | **378.177s** |
| Tool calls | 256.816s (68%) |
| LLM overhead | 121.361s (32%) |
| Output size | 16447 KB |
| Total tokens | 1,711,224 |
| Estimated cost | $0.9166 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.156s |
| skill_install | 11.851s |
| download_video | 0.135s |
| skill_run | 226.835s |
| — scene_detection | 3.762s |
| — music_generation_minimax | 163.0s |
| — beat_alignment | Nones |
| — audio_mix | Nones |
| — beat_sync_full | 226.835s |
| upload_output | 14.0s |

## Observations

Clean test. MiniMax music generation: 163.0s for 16.0s track (hype/120BPM trap). 26 scene cuts detected, sync mode auto-selected. Output 3.4x larger than input (HEVC→H.264 re-encode). Wall_total includes estimated 14s upload (wall_end recorded before upload call — timing note). Music generated inline in beat_sync_full step.
