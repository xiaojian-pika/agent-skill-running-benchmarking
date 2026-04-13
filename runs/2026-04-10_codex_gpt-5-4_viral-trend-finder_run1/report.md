# Viral Trend Finder Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `viral-trend-finder`
- Skill version: `f4f6db08c84a66db5fd06dee63eefb84cb36b25c`

## Input

- Test cases:
  - T1: `find "fitness" --platforms tiktok,instagram --count 5`
  - T2: `find "cooking" --platforms x --count 5`
  - T3: `analyze <first URL from T1>`
  - T4: `trending`
- T3 URL selected from T1: `https://www.instagram.com/p/DW6T0PKDLuQ/`
- Benchmark script: `/home/ec2-user/Pikabot/nova3-agent-skills/viral-trend-finder/scripts/viral_trend_finder.py`
- Environment notes: `ffmpeg` and `yt-dlp` were available; `PIKA_API_BASE_URL` and `PIKA_AGENT_API_KEY` were present; `GOOGLE_API_KEY` was missing but not required for this proxy-based run
- Skill-saved analysis output:
  - `/tmp/viral-trend-finder/2026-04-10-fitness-enthusiasts-and-busy-moms.json`

## Raw Timings

- `WALL_START`: `1775827225078207762`
- `t1_find_fitness`: `14882ms` (`exit=0`)
- `t2_find_cooking_x`: `3758ms` (`exit=0`)
- `t3_analyze`: `251893ms` (`exit=0`)
- `t4_trending`: `70421ms` (`exit=0`)
- `WALL_END`: `1775827705526420684`
- `wall_total`: `480448ms`

## Execution Summary

- T1 fitness search
  - results: `8`
  - top result: Instagram `58450` views
  - selected T3 URL: `https://www.instagram.com/p/DW6T0PKDLuQ/`
- T2 cooking on X
  - results: `10`
  - top result: X `2997629` views
  - top URL: `https://x.com/FitFusion__/status/2035004866750206216`
- T3 full analysis
  - title: `Instant Back Burn`
  - platform: `instagram`
  - viral formula: `Quick Fitness Fix × Accessible Equipment × Visual Countdown`
  - target niche: `fitness enthusiasts and busy moms`
  - format: `tutorial`
  - success factors: `6`
  - script segments: `10`
  - storyboard shots: `10`
- T4 general trending
  - results: `10`
  - top result: TikTok `32400000` views
  - top title: `Milk & White KitKat Cheesecake ...`

## T3 Stage Timings

- `metadata`: `1.13s`
- `download`: `11.74s`
- `frame_extract`: `5.59s`
- `gemini_vision`: `20.26s`
- `llm_synthesis`: `212.98s`

## T3 Pipeline Notes

- `yt-dlp` failed on the Instagram URL, and the skill successfully fell back to the Apify CDN download path.
- The downloaded video was `video.mp4` at about `32566 KB`.
- Frame extraction produced `177` frames, from which the skill sampled and analyzed `20` frames with Gemini Vision.
- `1/20` frame analyses failed, but the run continued and synthesis still completed.
- Anthropic synthesis hit two `ReadTimeout` retries and then the skill fell back to OpenAI, which completed successfully.

## Totals

- Tool/compute time: `340.954s`
- Estimated LLM overhead: `139.494213s`
- Skill/compute share: `70.965817%`
- LLM/overhead share: `29.034183%`

## Tokens And Cost

- Raw extractor reference: `python3 /home/ec2-user/Pikabot/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Benchmark token accounting used rollout `token_count` deltas between `WALL_START` and `WALL_END`, because the latest cumulative extractor output includes earlier turns in this Codex session.
- Input tokens: `4445638`
- Output tokens: `4285`
- Cached input tokens: `4062336`
- Cache write tokens: `null`
- Total tokens recorded in `result.json`: `8512259` (`input + output + cache_read`, matching the benchmark template convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$11.156945`

## Notes

- No install step: the skill already existed locally.
- No standalone asset acquisition step: T3 video download was part of the skill's execution pipeline.
- T3 dominated the benchmark runtime; its `llm_synthesis` stage alone was longer than the entire T1, T2, and most of T4 combined.
- T4's TikTok native trending mode returned zero results, so the skill automatically fell back to niche-based searches across `dance`, `lifestyle`, `comedy`, `food`, and `fitness`, then supplemented them with Instagram and X category searches.
- The run used `PIKABOT_STATE_DIR=/tmp` so the skill could persist outputs outside the default `/data/.pikabot` path.
