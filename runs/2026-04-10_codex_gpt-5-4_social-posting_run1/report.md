# Social Posting Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `social-posting`
- Skill version: `f4f6db08c84a66db5fd06dee63eefb84cb36b25c`

## Input

- Content brief: `video tutorial: how to cook perfect pasta at home — tested 5 different techniques`
- Benchmark cases:
  - `T1`: `--platform x --tone casual`
  - `T2`: `--platform instagram --tone casual`
  - `T3`: `--platform tiktok --tone funny`
  - `T4`: `--platform instagram --tone casual --variations 3`

## Raw Timings

- `WALL_START`: `1775831417817984288`
- `T1_x_casual`: `7699ms`
- `T2_instagram_casual`: `16242ms`
- `T3_tiktok_funny`: `6879ms`
- `T4_instagram_variations3`: `47022ms`
- `WALL_END`: `1775831606247518507`
- `wall_total`: `188429ms`

## Skill Output

- `T1` X casual:
  - `caption_len=226`
  - `hashtags_count=2`
  - `full_post_len=242`
  - preview: `tested 5 pasta techniques so you don't have to. salting the water less is actually fine. rinsing pasta is not the sin people say it is.`
- `T2` Instagram casual:
  - `caption_len=980`
  - `hashtags_count=25`
  - peak days: `Tuesday`, `Wednesday`
  - preview: `I was wrong about cooking pasta until I actually tested every method back to back 🍝`
- `T3` TikTok funny:
  - `caption_len=69`
  - `hashtags_count=4`
  - peak days: `Tuesday`, `Thursday`, `Friday`
  - preview: `I tested 5 pasta techniques so you don't have to (one made me cry fr)`
- `T4` Instagram variations=3:
  - `variations_returned=1` (`expected=3`)
  - `caption_len=843`
  - `hashtags_count=30`
  - preview: `I was wrong about pasta for literally 20 years and a nonna in my building finally called me out 😭`

## Internal LLM Timings

- `T1`: `⏱️ [llm] 7.6s`, `⏱️ [total] 7.6s`
- `T2`: `⏱️ [llm] 16.2s`, `⏱️ [total] 16.2s`
- `T3`: `⏱️ [llm] 6.8s`, `⏱️ [total] 6.8s`
- `T4`: first `⏱️ [llm] 30.0s` on the variations attempt, then `⚠️ Variations generation failed (LLM returned malformed JSON array...)`, then fallback `⏱️ [llm] 16.9s`, final `⏱️ [total] 46.9s`

## Totals

- Tool/compute time: `77.842s`
- Estimated LLM overhead: `110.587534s`
- Skill/compute share: `41.310934%`
- LLM/overhead share: `58.689066%`

## Tokens And Cost

- Token accounting source: Codex rollout usage deltas measured between the benchmark wall-start and wall-end timestamps
- Input tokens: `3122015`
- Output tokens: `2575`
- Cached input tokens: `2669696`
- Cache write tokens: `null`
- Total tokens recorded in `result.json`: `5794286` (sum of input + output + cache_read per the benchmark template/validator convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$7.830787`

## Notes

- No install step was needed because the skill already existed locally.
- No asset acquisition step was needed because the benchmark input is text-only.
- All four runs used API credentials sourced from `~/keys/.env` and the local skill via `PYTHONPATH=/home/ec2-user/Pikabot/nova3-agent-skills`.
- `T4` is the main behavioral anomaly in this run: the skill accepted `--variations 3`, but the Anthropic response for the variations pass was malformed JSON, so the script warned and returned a single Instagram caption via fallback instead of three distinct variations.
- The benchmark `llm_overhead_s` field is the harness-level remainder `wall_total - tool_calls`; it is not the same thing as the skill's internal `⏱️ [llm]` timings printed to stderr.
