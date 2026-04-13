# Benchmark Report: long-to-short-video on Managed Claude Agent

**Date:** 2026-04-10
**Platform:** managed-claude-agent (Anthropic managed container)
**Model:** Claude Sonnet 4.6
**Task:** T1 fresh 3-clip tiktok, T2 cache-hit rerun, T3 hormozi 3-clip fresh, T4 5-clip tiktok fresh
**Session:** sesn_011CZvNv4LbAYjNgcsX4PfJE

## Results

| Metric | Value |
|--------|-------|
| Wall total | **824.3s** (13m44s) |
| Tool execution (sum) | 701.7s (85.1%) |
| LLM overhead | 122.6s (14.9%) |
| Tokens (total) | 225,228 |
| Estimated cost | $0.246 |

## Timing Breakdown

| Phase | Tool time | LLM time | Total |
|-------|-----------|----------|-------|
| Init (check files, clean dirs) | 3.1s | 22.3s | 25.4s |
| T1 nohup launch + poll + parse | ~228s | ~15s | ~243s |
| T2 nohup launch + poll | ~10s | ~12s | ~22s |
| T3 nohup launch + poll + parse | ~213s | ~15s | ~228s |
| T4 nohup launch + poll (×2) + parse | ~256s | ~14s | ~270s |
| Final report synthesis | — | 37s | 37s |

## Per-Script Timing

| Test | Script total | S1 Apify | S1 Face | S2 Whisper | S3 LLM | S4-S7/clip | Clips |
|------|-------------|----------|---------|------------|--------|------------|-------|
| T1 tiktok fresh | **231.6s** | 37s | ~22s | 12s | 11s | ~50s | 3 |
| T2 cache hit | **7.8s** | 0s (hit) | 0s (hit) | 0s (hit) | 0s (hit) | 0s (hit) | 3 |
| T3 hormozi fresh | **217.1s** | 37s | ~22s | 12s | 9s | ~46s | 3 |
| T4 5-clip tiktok | **272.7s** | 53s | ~22s | 9s | 14s | ~44s | 4* |

*T4 requested 5 clips; LLM returned 4 (207s source video lacks 5 distinct high-quality segments).

## Clips Produced

| Test | Clip | Virality | Duration | CDN |
|------|------|----------|----------|-----|
| T1 | 1 | 8.7 | 59.18s | a89917de…/clip_01_final.mp4 |
| T1 | 2 | 7.9 | 43.62s | 43123cab…/clip_02_final.mp4 |
| T1 | 3 | 6.8 | 50.0s | e441b1aa…/clip_03_final.mp4 |
| T2 | 1–3 | same | same | identical CDN URLs (checkpoint) |
| T3 | 1 | 8.7 | 59.18s | d6a2fff4…/clip_01_final.mp4 |
| T3 | 2 | 7.2 | 45.16s | 89255365…/clip_02_final.mp4 |
| T3 | 3 | 5.0 | 45.0s | 2eb102a2…/clip_03_final.mp4 |
| T4 | 1 | 9.1 | 44.0s | 027b3942…/clip_01_final.mp4 |
| T4 | 2 | 8.2 | 43.62s | 54744f13…/clip_02_final.mp4 |
| T4 | 3 | 5.0 | 45.0s | 1372c100…/clip_03_final.mp4 |
| T4 | 4 | 5.0 | 45.0s | d70f9c6f…/clip_04_final.mp4 |

## Key Observations

- **MCA is ~1.9× faster than PikaBot per fresh run:** T1=231.6s vs PikaBot=442s; T3=217.1s vs PikaBot=442.7s. MCA container has faster ffmpeg/OpenCV processing (~44-50s/clip vs ~121s/clip on PikaBot EKS pods). S1 Apify times are consistent (37-53s across platforms).

- **nohup+poll pattern worked correctly:** All 3 fresh runs (T1/T3/T4) required nohup since they exceed the 295s bash timeout. Poll interval was 15s. T4 poll crashed once at 219.95s (container crash) — agent retried, found done file at 16:21:09. T4_ms (272.7s) was accurately measured from `/tmp/t4_start_ns.txt` saved at nohup launch.

- **Cache system fully functional:** T2 completed in 7.8s (29× speedup over T1). All 5 cache layers hit: video file, face timeline, transcript, LLM clip selections, rendered clips. Same CDN URLs returned.

- **T4 5→4 clip downgrade:** For a 207s video, 5 clips of ~45s each would require ~225s of content with no overlap. LLM correctly returned 4 clips (distinct segments: 9.1/8.2/5.0/5.0 virality). Same behavior observed on PikaBot and Claude Code.

- **S1 Apify variability:** T1/T3: 37s, T4: 53s (server 500 → retry). Consistent with other platforms (PikaBot T1: 36s, T3: 36s, T4: 52s).

- **S2 Whisper via proxy: 9-12s** for a 207s video. Very consistent across platforms.

- **S3 LLM clip selection: 9-14s** — fast and efficient regardless of clip count.

- **llm_pct = 14.9%** — consistent with other MCA media skills (VTF=13.2%, SAA orchestration=12.1%). LLM time here is orchestration-only (nohup launch calls, poll interpretation, final synthesis). Skill's internal Anthropic calls (S3) are inside the nohup process and counted in tool_calls_s.

- **Cost: $0.246** — significant cache_read (197K tokens). The long nohup poll outputs and multi-turn T1→T4 sequence generate more orchestration tokens than SP/SAA but less than PikaBot (which has 164K system_prompt_tokens per call).

- **Skill installed via init_script embed:** 7 scripts (83KB raw, 111KB b64) embedded inline. Nova3-common (nova3_common.config) mounted via skill_01WVFxRuNsjXYwW9Tz7Q2Nks. No Pika hub or zip upload needed.
