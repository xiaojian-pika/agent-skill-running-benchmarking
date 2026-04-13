# Video Translation Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `video-translation`
- Skill version: `eeb6d71d06851874623e505c94f7f80547c78925`

## Input

- File: `charli-daily-vlog.mp4`
- URL: `https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4`
- Resolution: `720x1280`
- Duration: `67.801995s`
- Codec: `hevc+aac`
- Size: `4790 KB`

## Raw Timings

- `WALL_START`: `1775803672202704429`
- `download_video`: `98ms`
- `probe_video`: `9ms`
- `skill_run`: `74306ms`
- `output_size`: `3368 KB`
- `WALL_END`: `1775803760766625183`
- `wall_total`: `88563ms`

## Skill Output

- Full script stage log:
  - `-> [0.0s] Extracting audio...`
  - `-> [1.2s] Transcribing audio (Whisper)...`
  - `-> [7.4s] Translating to 'es' (gpt-4o)...`
  - `-> [11.3s] Cloning voice from audio...`
  - `-> [15.4s] Generating TTS (eleven_v3)...`
  - `-> [31.8s] Replacing audio track...`
  - `Done: /tmp/bench_vt_output.mp4 (32s)`
- Transcript length: `691` chars
- Translated text length: `734` chars
- Cloned voice ID: `nRCuzgUNNvOsfGEmxMHv`
- TTS audio size: `699.6 KB`
- Voice cleanup completed after `Done:`: `Deleted cloned voice: nRCuzgUNNvOsfGEmxMHv`

## Totals

- Tool/compute time: `74.413s`
- Estimated LLM overhead: `14.15s`
- Skill/compute share: `84.022673%`
- LLM/overhead share: `15.977327%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Input tokens: `8394771`
- Output tokens: `30118`
- Cached input tokens: `7921792`
- Cache write tokens: `null`
- Extractor-reported total tokens: `8424889`
- Total tokens recorded in `result.json`: `16346681` (sum of input + output + cache_read per the benchmark template/validator convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$21.288107`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- The script’s stage log covers roughly the first `32s` of the pipeline; the measured `skill_run` was `74.306s`, so about `42.3s` elapsed after `Done:` was printed and before process exit. The most likely cause is cloned-voice cleanup in the script’s `finally` block.
- This benchmark used `--no-lip-sync`, so the final media step was ffmpeg audio replacement rather than fal lip sync.
