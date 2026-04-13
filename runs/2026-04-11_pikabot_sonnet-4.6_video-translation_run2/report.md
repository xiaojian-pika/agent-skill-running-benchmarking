# video-translation Benchmark — pikabot / Claude Sonnet 4.6 (anthropic/claude-sonnet-4-6)

**Date:** 2026-04-11
**Platform:** pikabot on EKS pod
**Skill:** video-translation 1.0.6

## Results

| Metric | Value |
|--------|-------|
| Wall total | **154.8s** |
| Tool calls | 67.91s (43.9%) |
| LLM overhead | 86.9s (56.1%) |
| Output size | 3328 KB |
| Total tokens | 1,860,372 |
| Estimated cost | $1.488233 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.156s |
| skill_install | 0.129s |
| subagent_start | 17.424s |
| download_video | 0.258s |
| skill_run | 35.377s |
| — extract_audio | 1.0s |
| — transcribe_waterfall | 3.0s |
| — translate_gpt4o | 2.0s |
| — voice_clone_elevenlabs | 1.9s |
| — tts_eleven_v3 | 24.9s |
| — replace_audio_ffmpeg | 2.2s |
| upload_output | 14.485s |

## Observations

v1.0.6 installed from CMS via direct API. rootPrefix='video-translation/' — flattened correctly. Spanish translation, no lip sync. Single pass: Whisper→translate→clone→TTS→replace. Voice cloned and deleted (GE6zLXa94V2gOOyfmQkM). TTS generated 674.7KB audio.
