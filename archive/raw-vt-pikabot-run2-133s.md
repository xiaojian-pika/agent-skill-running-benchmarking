============================================================
VIDEO-TRANSLATION E2E PERF LOG — PIKABOT (agent pod) — ROUND 2
============================================================
Date: 2026-04-09T17:53–17:56 UTC
Skill version: 1.0.4

PHASE 1 — INSTALL:
--------------------------------------------------
cms_fetch............................... 1.908s
skill_install (download+extract)........ 0.299s
subagent_session_start.................. ~2.0s (est.)

PHASE 2 — DOWNLOAD:
--------------------------------------------------
download_video.......................... 0.361s

PHASE 3 — SKILL EXECUTION:
--------------------------------------------------
probe_video............................. 0.686s
skill_run (translate_video.py).......... 41.963s
- extract_audio....................... (not individually timed)
- whisper_transcribe.................. (not individually timed)
- translate_gpt4o..................... (not individually timed)
- voice_clone_elevenlabs.............. (not individually timed)
- tts_eleven_v3....................... (not individually timed)
- replace_audio_ffmpeg................ (not individually timed)

PHASE 4 — DELIVERY:
--------------------------------------------------
upload_output (pika-upload-file)........ (not timed — tool call, no T wrap)

OVERHEAD:
--------------------------------------------------
LLM thinking (gaps between calls)....... ~87.8s

TOTALS:
--------------------------------------------------
TOOL_CALLS_TOTAL........................ ~45.2s
LLM_OVERHEAD_TOTAL...................... ~87.8s
WALL_TOTAL.............................. 133.052s

Output: https://msaocnoosm1a4.pika.art/v2/files/agent/ab4d4c5f-bea8-4226-b77a-af30f164f892/bench_vt_output.mp4
Output size: 2,756 KB
Input: 720×1280 HEVC/HE-AACv2, 67.8s @30fps, ~4,790 KB

Skill log:
-> Extracting audio...
-> Transcribing audio (Whisper)...
Transcribed 630 chars
-> Translating to 'es' (gpt-4o)...
Translated 647 chars
-> Cloning voice from audio...
Cloned voice: 4VyMidbT9JC6o0qN0Jub
-> Generating TTS (eleven_v3, voice=4VyMidbT9JC6o0qN0Jub)...
TTS audio: 556.0 KB
-> Replacing audio track...
Done: /tmp/bench_vt_output.mp4
Deleted cloned voice: 4VyMidbT9JC6o0qN0Jub
notes:

• skill_run 42s — fast, well within prior 39-56s range from skill test
• LLM overhead ~88s dominates wall time — 66% of 133s is agent thinking/scheduling, not tool execution. subagent spawning adds the biggest chunk here
• sub-step timings missing — translate_video.py doesn't emit per-step timestamps to stderr, so the breakdown rows are unavailable without script instrumentation
• upload not T-wrapped — step 7 was a pika-upload-file tool call in the subagent; no bash T variable wraps tool calls by design. upload time is baked into LLM overhead estimate
• voice cleanup confirmed — cloned voice 4VyMidbT9JC6o0qN0Jub deleted post-TTS :white_check_mark: