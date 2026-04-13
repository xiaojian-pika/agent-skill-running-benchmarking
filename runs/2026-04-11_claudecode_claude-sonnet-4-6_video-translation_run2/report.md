# Benchmark Report: video-translation — claudecode (Sonnet 4.6) — Run 2

**Date:** 2026-04-11
**Platform:** claudecode (claude-sonnet-4-6)
**Skill version:** f323b95
**Test input:** charli-daily-vlog.mp4 (67.8s, 4.9MB, HEVC+AAC)

## Summary

| Metric | Value |
|--------|-------|
| Wall total | 72.825s |
| Tool calls | 54.320s |
| LLM overhead | 18.505s (25.4%) |
| Output size | 3,272 KB |
| Target language | Spanish (es) |
| Estimated cost | $0.3565 |

## Timings

| Step | Time |
|------|------|
| Download video | 229ms |
| Probe video | 8ms |
| extract_audio | 1,100ms |
| whisper_transcribe (API) | 4,200ms |
| translate_gpt4o | 4,000ms |
| voice_clone_elevenlabs | 4,500ms |
| tts_eleven_v3 | 33,700ms |
| replace_audio_ffmpeg | 6,583ms |
| **Total tool calls** | **54,320ms** |
| **Wall total** | **72,825ms** |
| LLM overhead | 18,505ms |

## Key Findings

- **TTS step (33.7s) is again the dominant variance factor** — ElevenLabs eleven_v3 API latency ranges from 16.4s (run1) to 33.7s across runs. Highly non-deterministic.
- **LLM overhead 25.4%** — lower than run1's 48.5% because run1 had a failed first attempt that added wall time.
- Whisper transcription (4.2s) and GPT-4o translation (4.0s) are stable across runs.
- Output: 3,272 KB (run1: 3,368 KB) — similar range.

## Comparison: Run 1 vs Run 2

| Step | Run 1 | Run 2 |
|------|-------|-------|
| extract_audio | 1.2s | 1.1s |
| whisper_transcribe | 6.2s | 4.2s |
| translate_gpt4o | 3.9s | 4.0s |
| voice_clone_elevenlabs | 4.1s | 4.5s |
| tts_eleven_v3 | 16.4s | 33.7s |
| replace_audio_ffmpeg | 4.4s | 6.6s |
| skill_run total | 36.237s | 54.083s |
| wall total | 70.487s | 72.825s |
| LLM overhead | 34.167s (48.5%) | 18.505s (25.4%) |
| Estimated cost | null | $0.3565 |
