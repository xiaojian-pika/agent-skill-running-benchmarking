# Video Translation Benchmark Report

- Date: 2026-04-11
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `video-translation`
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

- `WALL_START`: `1775926391784766405`
- `download_video`: `247ms`
- `probe_video`: `9ms`
- `skill_run`: `49128ms`
- `output_size`: `3368 KB`
- `WALL_END`: `1775926455678766488`
- `wall_total`: `63894ms`

## Skill Output

- Full script stage log:
  - `-> [0.0s] Extracting audio...`
  - `-> [1.2s] Transcribing audio (Whisper → Deepgram → Gemini)...`
  - `Trying Whisper API...`
  - `Transcribed 690 chars (Whisper)`
  - `-> [5.7s] Translating to 'es' (gpt-4o)...`
  - `Translated 726 chars`
  - `-> [9.4s] Cloning voice from audio...`
  - `Cloned voice: 8oufHRD6dZfPizkfnDNz`
  - `-> [14.2s] Generating TTS (eleven_v3)...`
  - `TTS audio: 698.4 KB`
  - `-> [44.6s] Replacing audio track...`
  - `Done: /tmp/bench_vt_output.mp4 (45s)`
  - `Deleted cloned voice: 8oufHRD6dZfPizkfnDNz`

## Totals

- Tool/compute time: `49.384s`
- Estimated LLM overhead: `14.51s`
- Skill/compute share: `77.290669%`
- LLM/overhead share: `22.709331%`

## Tokens And Cost

- Source: `python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after 1775926391784 --before 1775926455678 --json`
- Input tokens: `771594`
- Output tokens: `1085`
- Cached input tokens: `756992`
- Cache write tokens: `null`
- Extractor-reported total tokens: `772679`
- Total tokens recorded in `result.json`: `772679` (matches the extractor-authoritative delta total)
- Estimated cost using `gpt-5.4` extract-codex-tokens.py methodology (input/output only; cache tokens informational): `$1.939835`

## Notes

- No install step: the skill already existed locally.
- No upload step: output stayed on local disk.
- The script's stage log covers roughly the first `45s` of the pipeline; the measured `skill_run` was `49.128s`, so about `4.1s` elapsed after `Done:` was printed and before process exit. This aligns with cloned-voice cleanup in the script's `finally` block.
- This benchmark used `--no-lip-sync`, so the final media step was ffmpeg audio replacement rather than fal lip sync.
