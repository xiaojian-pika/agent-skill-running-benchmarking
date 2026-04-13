# apple-music-reference Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** apple-music-reference 1.0.2

## Results

| Metric | Value |
|--------|-------|
| Wall total | **50.865s** |
| Tool calls | 4.246s (8%) |
| LLM overhead | 46.619s (92%) |
| Output size | 961 KB |
| Total tokens | 939,367 |
| Estimated cost | $0.3433 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.189s |
| skill_install | 1.944s |
| skill_run | 0.572s |
| — search_apple_music | 0.541s |
| — search_and_download_preview | 0.572s |
| upload_output | 1.0s |

## Observations

Clean test, no input video. Pure Apple Music API benchmark. Skill compute is trivially fast (<1s per call). LLM overhead dominates. No asset_acquisition phase. Wall_total includes estimated 1s upload.
