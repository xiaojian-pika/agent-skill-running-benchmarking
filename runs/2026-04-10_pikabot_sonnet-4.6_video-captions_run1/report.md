# video-captions Benchmark — pikabot / Claude Sonnet 4.6

**Date:** 2026-04-10
**Platform:** pikabot on EKS pod
**Skill:** video-captions 1.0.8

## Results

| Metric | Value |
|--------|-------|
| Wall total | **159.771s** |
| Tool calls | 82.275s (52%) |
| LLM overhead | 77.496s (48%) |
| Output size | 30726 KB |
| Total tokens | 1,294,824 |
| Estimated cost | $0.9616 |

## Timing breakdown

| Step | Time |
|------|------|
| cms_fetch | 0.179s |
| skill_install | 0.398s |
| download_video | 0.217s |
| skill_run | 30.397s |
| — extract_audio | 0.172s |
| — transcribe_faster_whisper | 24.733s |
| — caption_script_full | 30.397s |
| upload_output | 26.103s |

## Observations

Clean test run (all bench files reset to round 1 before run). faster-whisper pre-installed from prior session. No subagent used — benchmark ran directly in main session. Output 6.4x larger than input due to hevc→h264 re-encode.
