# Music Beat-Sync Benchmark Report

- Date: 2026-04-11
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `music-beat-sync`
- Skill version: `f323b95d010e0dfda2aacb8183ce250ff53eade5`
- Round: `2`

## Input

- File: `charli-daily-vlog.mp4`
- URL: `https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4`
- Resolution: `720x1280`
- Duration: `67.801995s`
- Codec: `hevc+aac`
- Size: `4790 KB`

## Raw Timings

- `WALL_START`: `1775926225308489292`
- `download_video`: `150ms`
- `probe_video`: `8ms`
- `scene_detection (26 cuts)`: `2365ms`
- `beat_sync_full`: `117846ms`
- `output_size`: `16448 KB`
- `WALL_END`: `1775926359151489877`
- `wall_total`: `133843ms`

## Skill Output

- Full script stdout: `/tmp/beat-sync/beat_sync_output.mp4`
- Dev log markers:
  - `S2` generated hype music at `120 BPM`
  - MiniMax music generation took `80.1s`
  - generated track duration: `16.6s`
  - `S4` detected `26` scene changes
  - auto-selected beat effect: `sync`
  - `S5` mixed audio in `replace` mode

## Totals

- Tool/compute time: `120.369s`
- Estimated LLM overhead: `13.474s`
- Skill/compute share: `89.93283%`
- LLM/overhead share: `10.06717%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after 1775926225308 --before 1775926359151 --json`
- Input tokens: `1014362`
- Output tokens: `1439`
- Cached input tokens: `1001600`
- Cache write tokens: `null`
- Extractor-reported total tokens: `1015801`
- Total tokens recorded in `result.json`: `1015801` (matches the extractor-authoritative delta total)
- Estimated cost using `gpt-5.4` extract-codex-tokens.py methodology (input/output only; cache tokens informational): `$2.550295`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- MiniMax generation dominated the full run and accounted for most of the measured compute time inside `beat_sync_full`.
- Internal substeps such as beat-alignment encoding and audio mixing were not individually timed by the benchmark prompt, so they remain `null` in the step list and are described from the dev log instead.
