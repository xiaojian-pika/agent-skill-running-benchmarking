# Benchmark Report: video-translation — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** Translate charli-daily-vlog.mp4 (720x1280, 67.8s) to Spanish, no lip sync
**Result:** SUCCESS — 3368 KB output

## Timing Summary

| Step | Time |
|------|------|
| Download video (S3 → devbox) | 0.074s |
| ffprobe | 0.009s |
| extract_audio | 1.2s |
| whisper_transcribe | 6.2s |
| translate_gpt4o | 3.9s |
| voice_clone_elevenlabs | 4.1s |
| tts_eleven_v3 | 16.4s |
| replace_audio_ffmpeg | 4.4s |
| **skill_run total** | **36.237s** |
| **Total tool calls** | **36.320s** |
| **LLM overhead** | **34.167s** |
| **Wall total** | **70.487s** |

- LLM overhead: 48.5% of wall time
- Skill/tool execution: 51.5% of wall time

## Observations

- **TTS is the bottleneck:** eleven_v3 took 16.4s (45% of skill time) — consistent with the 15-30s noted in benchmark docs.
- **Whisper is the second biggest:** 6.2s for 691 chars of English speech from a 67.8s video.
- **API chain is tight:** 5 of 6 sub-steps are network calls (Whisper, GPT-4o, ElevenLabs clone, ElevenLabs TTS, ffmpeg local). All succeeded on first try.
- **LLM overhead much higher here (48.5%)** than video-captions (30%) or music-beat-sync (18%). The skill itself is faster (36s vs 121-150s), making LLM overhead proportionally larger.
- **Short output:** 3368 KB vs 4915 KB input — expected, TTS audio is lower bitrate than original.
- **Voice clone cleanup worked:** Voice nRCuzgUNNvOsfGEmxMHv auto-deleted after use.
- **PYTHONPATH caveat:** Tilde `~` does not expand in multi-line env var assignments in Bash; must use explicit `/home/mingzhi/` path.
