# Apple Music Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `apple-music-reference`
- Skill version: `eeb6d71d06851874623e505c94f7f80547c78925`

## Input

- Query: `bohemian rhapsody queen`
- Input type: Apple Music search query only

## Raw Timings

- `WALL_START`: `1775803971502608822`
- `search_apple_music`: `744ms`
- `search_and_download`: `544ms`
- `preview_size`: `964 KB`
- `WALL_END`: `1775803986481129586`
- `wall_total`: `14978ms`

## Search Output

- Search-only result count: `5`
- Top result:
  - title: `Bohemian Rhapsody`
  - artist: `Queen`
  - album: `Greatest Hits I, II & III: The Platinum Collection`
  - duration: `355s`
  - song id: `1440650711`
- Downloaded file: `/tmp/bench_am_preview.m4a`
- File type: `ISO Media, Apple iTunes ALAC/AAC-LC (.M4A) Audio`

## Totals

- Tool/compute time: `1.288s`
- Estimated LLM overhead: `13.69s`
- Skill/compute share: `8.599279%`
- LLM/overhead share: `91.400721%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Input tokens: `10304893`
- Output tokens: `36412`
- Cached input tokens: `9634176`
- Cache write tokens: `null`
- Extractor-reported total tokens: `10341305`
- Total tokens recorded in `result.json`: `19975481` (sum of input + output + cache_read per the benchmark template/validator convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$26.126352`

## Notes

- No install step: the skill already existed locally.
- No asset download step: the benchmark input is a query, not a file.
- No upload step: the preview remained on local disk.
- This benchmark is very short and API-bound, so the wall time is dominated by orchestration overhead rather than the two script calls.
