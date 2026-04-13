# Music Beat-Sync Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `music-beat-sync`
- Skill version: `eeb6d71d06851874623e505c94f7f80547c78925`

## Input

- File: `charli-daily-vlog.mp4`
- URL: `https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4`
- Resolution: `720x1280`
- Duration: `67.801995s`
- Codec: `hevc+aac`
- Size: `4790 KB`

## Raw Timings

- `WALL_START`: `1775803170573418152`
- `download_video`: `133ms`
- `probe_video`: `9ms`
- `scene_detection (26 cuts)`: `2503ms`
- `beat_sync_full`: `91205ms`
- `output_size`: `16432 KB`
- `WALL_END`: `1775803345173874250`
- `wall_total`: `174600ms`

## Skill Output

- Full script stdout: `/tmp/beat-sync/beat_sync_output.mp4`
- Dev log markers:
  - `S2` generated hype music at `120 BPM`
  - MiniMax music generation took `51.6s`
  - generated track duration: `22.2s`
  - `S4` detected `26` scene changes
  - auto-selected beat effect: `sync`
  - `S5` mixed audio in `replace` mode

## Totals

- Tool/compute time: `93.85s`
- Estimated LLM overhead: `80.75s`
- Skill/compute share: `53.751432%`
- LLM/overhead share: `46.248568%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Input tokens: `4466951`
- Output tokens: `21994`
- Cached input tokens: `4224000`
- Cache write tokens: `null`
- Extractor-reported total tokens: `4488945`
- Total tokens recorded in `result.json`: `8712945` (sum of input + output + cache_read per the benchmark template/validator convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$11.387317`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- MiniMax generation dominated the full run and accounted for most of the measured compute time inside `beat_sync_full`.
- Internal substeps such as beat-alignment encoding and audio mixing were not individually timed by the benchmark prompt, so they remain `null` in the step list and are described from the dev log instead.
