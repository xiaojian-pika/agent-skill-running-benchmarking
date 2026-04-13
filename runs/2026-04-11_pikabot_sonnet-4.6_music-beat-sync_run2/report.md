# music-beat-sync Benchmark — pikabot / Claude Sonnet 4.6 (anthropic/claude-sonnet-4-6)

**Date:** 2026-04-11
**Platform:** pikabot on EKS pod
**Skill:** music-beat-sync 1.0.6

## Results

| Metric | Value |
|--------|-------|
| Wall total | **324.52s** |
| Tool calls | 226.11s (69.7%) |
| LLM overhead | 98.41s (30.3%) |
| Output size | 16388 KB |
| Total tokens | 2,291,425 |
| Estimated cost | $1.070076 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.218s |
| skill_install | 0.125s |
| subagent_start | 14.287s |
| download_video | 0.155s |
| skill_run | 191.743s |
| — scene_detection | 3.719s |
| — music_generation_minimax | 128.2s |
| — beat_alignment | Nones |
| — audio_mix | Nones |
| — beat_sync_full | 191.743s |
| upload_output | 15.784s |

## Observations

v1.0.6 installed from CMS via direct API call. rootPrefix='' but zip contained music-beat-sync/ subfolder — manual flatten needed. hype vibe @ 120 BPM. Music generation (MiniMax) took 128.2s for 16.5s track. Short track issue observed (previous finding confirmed).
