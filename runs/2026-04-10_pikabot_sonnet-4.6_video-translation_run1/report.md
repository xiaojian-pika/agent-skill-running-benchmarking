# video-translation Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** video-translation 1.0.5

## Results

| Metric | Value |
|--------|-------|
| Wall total | **105.961s** |
| Tool calls | 38.247s (36%) |
| LLM overhead | 67.714s (64%) |
| Output size | 2902 KB |
| Total tokens | 1,124,295 |
| Estimated cost | $0.7328 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.227s |
| skill_install | 1.766s |
| download_video | 0.366s |
| skill_run | 31.81s |
| — extract_audio | 1.0s |
| — whisper_transcribe | 3.2s |
| — translate_gpt4o | 2.1s |
| — voice_clone_elevenlabs | 4.9s |
| — tts_eleven_v3 | 18.5s |
| — replace_audio_ffmpeg | 1.3s |
| upload_output | 4.0s |

## Observations

Clean test. No errors — single-pass run. Voice clone auto-cleaned up post-run. Output smaller than input (HEVC→AAC audio replacement, no video re-encode). TTS is dominant bottleneck (61.6% of translate pipeline). Wall_total includes estimated 4s upload (wall_end recorded before upload call).
