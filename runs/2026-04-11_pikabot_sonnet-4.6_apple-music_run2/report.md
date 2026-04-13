# apple-music-reference Benchmark — pikabot / Claude Sonnet 4.6 (anthropic/claude-sonnet-4-6)

**Date:** 2026-04-11
**Platform:** pikabot on EKS pod
**Skill:** apple-music-reference 1.0.2

## Results

| Metric | Value |
|--------|-------|
| Wall total | **96.98s** |
| Tool calls | 31.56s (32.5%) |
| LLM overhead | 65.43s (67.5%) |
| Output size | 961 KB |
| Total tokens | 1,926,366 |
| Estimated cost | $2.053471 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.111s |
| skill_install | 0.135s |
| subagent_start | 16.381s |
| skill_run | 0.553s |
| — search_apple_music | 0.438s |
| — search_and_download_preview | 0.553s |
| upload_output | 13.939s |

## Observations

v1.0.2 from CMS. rootPrefix='' but zip had apple-music-reference/ subfolder — manual flatten required (same pattern as music-beat-sync). No video input — search query only. Search returned 5 results; top pick: Bohemian Rhapsody by Queen (Greatest Hits I,II&III).
