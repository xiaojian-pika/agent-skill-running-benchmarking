# Long To Short Video Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `long-to-short-video`
- Skill version: `f4f6db08c84a66db5fd06dee63eefb84cb36b25c`

## Input

- Source: `https://www.youtube.com/watch?v=UNP03fDSj1U`
- Title: `Try something new for 30 days - Matt Cutts`
- Measured source duration: `207.3s`
- Benchmark cases:
  - `T1`: fresh `--num-clips 3 --style tiktok --out /tmp/lts_t1 --dev`
  - `T2`: cache-hit rerun with same `--out /tmp/lts_t1 --dev`
  - `T3`: fresh `--num-clips 3 --style hormozi --out /tmp/lts_t3 --dev`
  - `T4`: fresh `--num-clips 5 --style tiktok --out /tmp/lts_t4 --dev`

## Raw Timings

- `WALL_START`: `1775835538925086125` (`2026-04-10T15:38:58.925086+00:00`)
- `T1_fresh_3clips_tiktok`: `335385ms`
- `T2_cache_hit`: `193ms`
- `T3_hormozi_3clips`: `372156ms`
- `T4_5clips_tiktok`: `406696ms`
- `WALL_END`: `1775836864445962335` (`2026-04-10T16:01:04.445962+00:00`)
- `wall_total`: `1325520ms`

## Stage Highlights

- `T1` fresh 3-clip TikTok:
  - `S1` used `dc_solutions~youtube-downloader-pro`, reached `SUCCEEDED` in `57s`, then downloaded `8MB` in `0s`
  - `S2` transcribed `3m27s` to `483 words` in `9s`
  - `S3` selected `3 clips` with scores `8.7, 7.9, 7.2` in `10s`
  - all 3 clips uploaded successfully
- `T2` cache hit:
  - `S1` video cache hit confirmed
  - face timeline loaded from cache (`104 samples`)
  - transcript loaded from cache (`483 words`)
  - clip selection loaded from cache and all 3 clips loaded from checkpoints
  - total rerun time was only `193ms`
- `T3` fresh 3-clip Hormozi:
  - `S1` actor succeeded in `50s`
  - `S2` transcription took `11s`
  - `S3` selected `3 clips` with scores `8.7, 7.8, 6.9` in `10s`
  - all 3 clips uploaded successfully
- `T4` fresh 5-clip TikTok:
  - `S1` actor succeeded in `43s`
  - `S2` transcription took `8s`
  - `S3` was asked for `5 clips` but selected only `4 clips` with scores `8.8, 7.1, 5.0, 5.0` in `12s`
  - clip 3 required an intro trim of `1.0s`
  - clip 4 start was snapped from `45.0s` to `48.0s` to avoid a no-face interval
  - final output contained `4` clips, not `5`

## Skill Output

- `T1`:
  - `success=true`, `num_clips=3`
  - top clip virality: `8.7`
  - clip 1 CDN: `https://msaocnoosm1a4.pika.art/v2/files/agent/83813f97-5441-4258-89b2-21b9c4f2f79d/clip_01_final.mp4`
- `T2`:
  - `success=true`, `num_clips=3`
  - output matched cached T1 results and reused the same CDN URLs
- `T3`:
  - `success=true`, `num_clips=3`
  - top clip virality: `8.7`
  - clip 1 duration increased to `59.18s` under the Hormozi selection path
- `T4`:
  - `success=true`, `num_clips=4`
  - requested clips: `5`
  - top clip virality: `8.8`
  - clip 1 CDN: `https://msaocnoosm1a4.pika.art/v2/files/agent/2384eeba-9e5b-4a92-90e1-e8aa1bbd2b3e/clip_01_final.mp4`

## Totals

- Tool/compute time: `1114.43s`
- Estimated LLM overhead: `211.09s`
- Skill/compute share: `84.074929%`
- LLM/overhead share: `15.925071%`

## Tokens And Cost

- Token accounting source: Codex rollout usage deltas measured between the benchmark wall-start and wall-end timestamps
- Input tokens: `1736227`
- Output tokens: `4370`
- Cached input tokens: `1635712`
- Cache write tokens: `null`
- Total tokens recorded in `result.json`: `3376309` (sum of input + output + cache_read per the benchmark template/validator convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$4.384268`

## Notes

- No install step was needed because the skill already existed locally.
- Asset acquisition is `null` in the benchmark schema because download happens internally in `S1`.
- Fresh runs used the `dc_solutions~youtube-downloader-pro` actor rather than `scraper_one~yt-downloader`.
- Fresh runs emitted repeated non-fatal ffmpeg/h264 `mmco: unref short failure` messages during face timeline scanning, but clip generation still completed successfully.
- The local `python3` preflight environment lacked `cv2`, but the actual benchmark used `python3.11`, where face detection worked and produced `S5 Face trajectory` logs for all fresh runs.
- The benchmark `llm_overhead_s` field is the harness-level remainder `wall_total - tool_calls`; it is not the same thing as the skill's internal `S3` clip-selection duration.
