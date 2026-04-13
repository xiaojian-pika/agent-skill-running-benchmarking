============================================================
VIDEO-TRANSLATION E2E PERF LOG — PIKABOT (agent pod) — ROUND 2
============================================================
Date: 2026-04-09T17:53–17:55 UTC
Skill version: 1.0.4

PHASE 1 — INSTALL:
--------------------------------------------------
 cms_fetch............................... 0.383s
 skill_install (download+extract)........ 0.164s
 subagent_session_start.................. N/A (ran inline per test rules)

PHASE 2 — DOWNLOAD:
--------------------------------------------------
 download_video.......................... 0.338s

PHASE 3 — SKILL EXECUTION:
--------------------------------------------------
 probe_video............................. 0.080s
 skill_run (translate_video.py).......... 27.504s
   - extract_audio....................... ~1.0s  ([0.0s]→[1.0s])
   - whisper_transcribe.................. ~2.2s  ([1.0s]→[3.2s])
   - translate_gpt4o..................... ~2.1s  ([3.2s]→[5.3s])
   - voice_clone_elevenlabs.............. ~1.8s  ([5.3s]→[7.1s])
   - tts_eleven_v3....................... ~18.3s ([7.1s]→[25.4s])
   - replace_audio_ffmpeg................ ~0.6s  ([25.4s]→[26s])

PHASE 4 — DELIVERY:
--------------------------------------------------
 upload_output (pika-upload-file)........ ~2s (estimated; no exec timer for tool call)

OVERHEAD:
--------------------------------------------------
 LLM thinking (gaps between calls)....... ~64.5s (wall - measured tools)

TOTALS:
--------------------------------------------------
 TOOL_CALLS_TOTAL........................ ~30.5s  (383+164+338+80+27504+~2000ms)
 LLM_OVERHEAD_TOTAL...................... ~64.5s
 WALL_TOTAL.............................. 94.936s

Output: https://cdn.pika.art/v2/files/agent/b3ecbffe-8ab7-4638-868e-b4a323ff3947/bench_vt_output.mp4
Output size: 3188 KB
Input size: 4.7 MB (67.8s, 720×1280 HEVC, HE-AACv2)

Skill log:
-> [0.0s] Extracting audio...
-> [1.0s] Transcribing audio (Whisper)...
   Transcribed 630 chars
-> [3.2s] Translating to 'es' (gpt-4o)...
   Translated 652 chars
-> [5.3s] Cloning voice from audio...
   Note: voice clone uses a single speaker model — multi-speaker videos will use the dominant voice
   Cloned voice: l0yO3GIxOYVQFppjdVDi
-> [7.1s] Generating TTS (eleven_v3)...
   TTS audio: 636.0 KB
-> [25.4s] Replacing audio track...
Done: /tmp/bench_vt_output.mp4 (26s)
   Deleted cloned voice: l0yO3GIxOYVQFppjdVDi

NOTES:
- Dominant cost is ElevenLabs TTS generation: 18.3s of 27.5s total skill time (66%)
- Wall time dominated by LLM overhead (~68%) — purely model thinking between sequential exec steps
- Step 2 had one failed attempt (source: not found in sh; retry with bash resolved it) — not included in timing
- No lip-sync step run (--no-lip-sync flag used)
- Voice clone was created and cleaned up correctly (ephemeral clones)
