# video-captions Benchmark — pikabot / Claude Sonnet 4.6 (anthropic/claude-sonnet-4-6)

**Date:** 2026-04-11
**Platform:** pikabot on EKS pod
**Skill:** video-captions 1.0.9

## Results

| Metric | Value |
|--------|-------|
| Wall total | **135.67s** |
| Tool calls | 51.47s (37.9%) |
| LLM overhead | 84.2s (62.1%) |
| Output size | 30752 KB |
| Total tokens | 1,760,813 |
| Estimated cost | $2.491001 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.117s |
| skill_install | 0.162s |
| subagent_start | 14.631s |
| download_video | 0.193s |
| skill_run | 18.655s |
| — caption_script_full | 18.655s |
| — extract_audio | Nones |
| — whisper_api_transcribe | Nones |
| — fix_word_timings | Nones |
| — generate_ass | Nones |
| — ffmpeg_burn | Nones |
| upload_output | 17.628s |

## Observations

v1.0.9 installed from CMS via direct API call (GET /api/hub/install?id=video-captions). Proxy API waterfall transcription (Whisper → Deepgram → Gemini) active — no local faster-whisper. Significant perf improvement vs round 1 (local whisper): 18.7s vs 29.1s script runtime.
