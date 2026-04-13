# Video Captions Benchmark Report

- Date: 2026-04-11
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `video-captions`
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

- `WALL_START`: `1775926167499519081`
- `download_video`: `271ms`
- `probe_video`: `9ms`
- `caption_script_full`: `11339ms`
- `output_size`: `30712 KB`
- `WALL_END`: `1775926190358207711`
- `wall_total`: `22858ms`

## Skill Output

- Output video: `/tmp/bench_vc_captioned.mp4`
- Sidecar ASS: `/tmp/bench_vc_captioned.ass`
- Script markers:
  - `Style: tiktok`
  - `132 words`
  - `720x1280, 67.8s`
  - `Saved: /tmp/bench_vc_captioned.ass`
  - `Done: /tmp/bench_vc_captioned.mp4`

## Totals

- Tool/compute time: `11.619s`
- Estimated LLM overhead: `11.239s`
- Skill/compute share: `50.831218%`
- LLM/overhead share: `49.168782%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after 1775926167499 --before 1775926190358 --json`
- Input tokens: `372894`
- Output tokens: `888`
- Cached input tokens: `296192`
- Cache write tokens: `null`
- Extractor-reported total tokens: `373782`
- Total tokens recorded in `result.json`: `373782` (matches the extractor-authoritative delta total)
- Estimated cost using `gpt-5.4` extract-codex-tokens.py methodology (input/output only; cache tokens informational): `$0.941115`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- The current prompt benchmarks only the full script path, not standalone transcription timing.
