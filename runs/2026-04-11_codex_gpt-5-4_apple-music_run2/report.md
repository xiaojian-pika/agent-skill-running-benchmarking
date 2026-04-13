# Apple Music Benchmark Report

- Date: 2026-04-11
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `apple-music-reference`
- Skill version: `f323b95d010e0dfda2aacb8183ce250ff53eade5`
- Round: `2`

## Input

- Query: `bohemian rhapsody queen`
- Input type: Apple Music search query only

## Raw Timings

- `WALL_START`: `1775926500617230912`
- `search_apple_music`: `545ms`
- `search_and_download`: `520ms`
- `preview_size`: `964 KB`
- `WALL_END`: `1775926513407217175`
- `wall_total`: `12789ms`

## Search Output

- Search-only result count: `5`
- Top result:
  - title: `Bohemian Rhapsody`
  - artist: `Queen`
  - album: `Greatest Hits I, II & III: The Platinum Collection`
  - duration: `355.145s`
  - song id: `1440650711`
- Downloaded file: `/tmp/bench_am_preview.m4a`

## Totals

- Tool/compute time: `1.065s`
- Estimated LLM overhead: `11.724s`
- Skill/compute share: `8.327469%`
- LLM/overhead share: `91.672531%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after 1775926500617 --before 1775926513407 --json`
- Input tokens: `426849`
- Output tokens: `979`
- Cached input tokens: `424192`
- Cache write tokens: `null`
- Extractor-reported total tokens: `427828`
- Total tokens recorded in `result.json`: `427828` (matches the extractor-authoritative delta total)
- Estimated cost using `gpt-5.4` extract-codex-tokens.py methodology (input/output only; cache tokens informational): `$1.076912`

## Notes

- No install step: the skill already existed locally.
- No asset download step: the benchmark input is a query, not a file.
- No upload step: the preview remained on local disk.
- This benchmark is very short and API-bound, so wall time is dominated by orchestration overhead rather than the two script calls.
