# Short Ads Benchmark — Run 1 Report

**Platform:** pikabot  
**Model:** claude-sonnet-4-6  
**Thinking level:** medium  
**Date:** 2026-04-23  
**Test case:** TC-01 — Crispello apple-honey sandwich ad, 30s 16:9

---

## Summary

| Metric | Value |
|---|---|
| **Status** | ✅ Completed |
| **Wall time** | 9.7 min (791.5s) |
| **LLM overhead** | 152.6s (19.3%) |
| **Skill/tool time** | 639.0s (80.7%) |
| **Output** | 30.08s MP4, 20.3 MB, 1280×720 |
| **Est. cost** | $0.89 |

---

## Output Quality

| Aspect | Assessment |
|---|---|
| **Video** | 2×15s acts concatenated, SeeDance r2v generation, border fix applied |
| **Audio** | BGM: 34.2s jazz/marimba instrumental (MiniMax music-2.5) |
| **VO** | "Made with wonder." via Brian voice (ElevenLabs), placed at 27.7s |
| **Encode** | H.264 CRF 16, AAC 192k, proper audio mix with fade in/out |

---

## Phase Breakdown

### Install (9.5s)
- Subagent spawn overhead: ~5s
- SKILL.md read: 4.46s
- Tokens: 3 in / 99 out

### Asset Acquisition (24.3s)
- Parse brief + concept pitch: 10.7s
- Brand tone profile: 7.5s
- Confirm direction: 6.1s
- Tokens: 3 in / 520 out
- No downloads (local images used)

### Execution (740.8s)
| Step | Duration | Notes |
|---|---|---|
| Visual script | 45s | 8-shot storyboard, 4 shots/act |
| SeeDance Act 1 | 430s | 15s video, 8.9MB, parallel |
| SeeDance Act 2 | 408s | 15s video, 7.4MB, parallel |
| BGM (MiniMax) | 73s | 34.2s jazz/marimba, hex decode patch applied |
| VO (ElevenLabs) | 1s | Brian voice, "Made with wonder." |
| Concat + encode | 70s | ffmpeg concat, border fix, audio mix |

- LLM overhead: 118.6s
- Tool calls: 639.0s
- Tokens: 14 in / 4841 out

### Delivery (17.2s)
- Final report: 12.2s
- Tokens: 1 in / 497 out
- Output: local file (no CDN in benchmark mode)

---

## Issues Encountered

| Issue | Severity | Resolution |
|---|---|---|
| **MiniMax BGM API** | Medium | API returned inline hex audio (`data.audio`) instead of URL (`data.audio_url`). Patched `gen_bgm.py` to decode hex bytes directly. BGM saved successfully (34.2s). |
| **No logo image** | Low | No brand logo provided. Brand lock shot used product hero instead. Pipeline completed without issue. |

---

## Token Summary

| Type | Count |
|---|---|
| Input tokens | 22 |
| Output tokens | 5,546 |
| Cache read | 502,597 |
| Cache write | 174,015 |
| **Total** | **682,180** |

---

## Cost Estimate

| Model | Rate | Tokens | Cost |
|---|---|---|---|
| claude-sonnet-4-6 | $3/M input | 22 | $0.0001 |
| claude-sonnet-4-6 | $15/M output | 5,546 | $0.0832 |
| claude-sonnet-4-6 | $0.30/M cache read | 502,597 | $0.1508 |
| claude-sonnet-4-6 | $3.75/M cache write | 174,015 | $0.6526 |
| **Total** | | | **$0.8867** |

---

## Conclusion

**Status: ✅ Ship**

The short-ads skill successfully completed a full 30s product ad generation in ~9.7 minutes. The pipeline executed all stages correctly:

1. ✅ Concept pitch and brand tone profile generated
2. ✅ 2-act visual script with proper shot size scheduling
3. ✅ SeeDance r2v parallel generation (both acts ~7 min)
4. ✅ BGM generated (MiniMax, with hex decode patch)
5. ✅ VO generated (ElevenLabs Brian)
6. ✅ Final encode with border fix and audio mix

**Key metrics:**
- Wall time: 791.5s
- LLM overhead: 19.3%
- Skill/tool time: 80.7%
- Output quality: 30s 720p MP4, 20.3 MB
- Cost: ~$0.89

**One fix needed:** The MiniMax BGM generator should handle inline `audio` hex data as a fallback when `audio_url` is not present.
