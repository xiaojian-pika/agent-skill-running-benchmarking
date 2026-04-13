# Video Captions Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `video-captions`
- Skill version: `eeb6d71d06851874623e505c94f7f80547c78925`

## Input

- File: `charli-daily-vlog.mp4`
- URL: `https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4`
- Resolution: `720x1280`
- Duration: `67.801995s`
- Codec: `hevc+aac`
- Size: `4790 KB`

## Raw Timings

- `WALL_START`: `1775802651330922273`
- `download_video`: `328ms`
- `probe_video`: `9ms`
- `extract_audio`: `408ms`
- `transcribe`: `21668ms`
- `caption_script_full`: `29388ms`
- `output_size`: `30720 KB`
- `WALL_END`: `1775802717747304425`
- `wall_total`: `66416ms`

## Skill Output

- Standalone transcription: `language=en words=138`
- Full script status:
  - style `tiktok`
  - generated `/tmp/bench_vc_captioned.ass`
  - generated `/tmp/bench_vc_captioned.mp4`
  - internal detection: `Detected language: en`

## Totals

- Tool/compute time: `51.801s`
- Estimated LLM overhead: `14.615s`
- Skill/compute share: `77.99476%`
- LLM/overhead share: `22.00524%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Input tokens: `2315604`
- Output tokens: `14919`
- Cached input tokens: `2118272`
- Cache write tokens: `null`
- Total tokens recorded in `result.json`: `4448795` (sum of input + output + cache_read per the benchmark template)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$5.9382`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- The faster-whisper small model cache already existed at `~/.cache/faster-whisper/models--Systran--faster-whisper-small`, so this run did not include a first-time model download.
- The token extractor reports latest-rollout session usage after the benchmark. The benchmark JSON uses the extractor's input/output/cache-read values and computes `tokens.total_tokens` as the sum requested by the benchmark template.
