# Social Account Analyzer Benchmark Report

- Date: 2026-04-10
- Platform: codex
- Runtime: Codex sandbox
- Model: gpt-5.4
- Skill: `social-account-analyzer`
- Skill version: `f4f6db08c84a66db5fd06dee63eefb84cb36b25c`

## Input

- Handles: `@natgeo` on Instagram, `@NASA` on X/Twitter, `@khaby.lame` on TikTok
- Benchmark script: `/home/ec2-user/Pikabot/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py`
- Environment notes: local Python 3.11 venv with `httpx`; `PIKABOT_STATE_DIR=/tmp`; API credentials sourced from `~/keys/.env`
- Skill-saved reports:
  - `/tmp/social-account-analyzer/2026-04-10-natgeo.json`
  - `/tmp/social-account-analyzer/2026-04-10-NASA.json`
  - `/tmp/social-account-analyzer/2026-04-10-khaby.lame.json`

## Raw Timings

- `WALL_START`: `1775819490941515862`
- `t1_instagram`: `102928ms` (`exit=0`)
- `t2_x`: `75509ms` (`exit=0`)
- `t3_tiktok`: `87300ms` (`exit=0`)
- `WALL_END`: `1775819807788464515`
- `wall_total`: `316846ms`

## Skill Stage Timings

- T1 Instagram `@natgeo`
  - `fetch`: `27.4s`
  - `llm`: `75.4s`
  - `total`: `102.8s`
- T2 X `@NASA`
  - `fetch`: `6.0s`
  - `llm`: `69.4s`
  - `total`: `75.4s`
- T3 TikTok `@khaby.lame`
  - `fetch`: `13.8s`
  - `llm`: `73.3s`
  - `total`: `87.2s`

## Account Output Details

### T1 Instagram `@natgeo`

- Followers: `274960878`
- Niche: `Science, Nature & Exploration Photography/Documentary`
- Audience persona: globally distributed `25–54` audience interested in science, wildlife, conservation, and adventure travel
- Engagement: `0.03%` (`average` for this follower tier)
- Benchmark context: mega-account Instagram ER is typically `0.01%–0.05%`; NatGeo sat around the middle of that band, while Artemis II carousel posts reached roughly `0.13%–0.24%`
- Posting frequency: `3.8/week`
- Best content type: `Carousel`
- Best posting days: `Monday`, `Tuesday`
- Trend: `stable`
- Top-performing themes:
  - `Space exploration / Artemis II`
  - `Wildlife defense behavior`
- Major content gaps:
  - no Reels/video-native strategy in the sampled set
  - limited behind-the-scenes creator/process storytelling
  - no interactive/community prompts
- Top posts:
  - `CAROUSEL_ALBUM` `0.1352%` ER: Artemis II record-breaking lunar flyby
  - `CAROUSEL_ALBUM` `0.1078%` ER: solar eclipse seen from the far side of the Moon
  - `IMAGE` `0.041%` ER: Kilauea lava patterns
- Growth opportunities:
  - Reels launch
  - sequel/series carousel publishing
  - interactive engagement mechanics
  - behind-the-lens content series
- First recommendation:
  - launch a first Reel using existing high-drama wildlife or volcanic footage with a curiosity-gap opening
- Calendar preview count: `4`
- Internal note: public-only Instagram data; the skill suggested that connecting the account would unlock reach, impressions, saves, and story insights
- Runtime anomaly:
  - Pass 2 logged `LLM JSON truncated, attempting repair...` and then recovered successfully

### T2 X `@NASA`

- Followers: `90943570`
- Niche: `Space Exploration & Science`
- Audience persona: primarily English-speaking `18–45` audience interested in science, astronomy, and technology
- Engagement: `0.03%` (`average` for this follower tier)
- Benchmark context: for `90M+` X accounts, `0.02%–0.05%` ER is typical; major mission posts can spike `5–10x` above baseline
- Posting frequency: `20.0/week`
- Best content type: `Video`
- Best posting days: `Thursday`, `Friday`
- Trend: `growing`
- Top-performing themes:
  - mission milestones and countdowns
  - astronaut POV / Earth-Moon imagery
- Major content gaps:
  - no standalone mission data infographics
  - no behind-the-scenes ground crew footage
  - underused multi-tweet mission narrative threads
- Top posts:
  - `VIDEO` `0.149%` ER: halfway point between Moon and Earth
  - `VIDEO` `0.1233%` ER: mission return coverage
  - `VIDEO` `0.0639%` ER: crescent Earth imagery from lunar distance
- Growth opportunities:
  - mission milestone live countdowns
  - behind-the-scenes ground crew videos
  - mission stat infographic posts
  - multi-tweet mission narrative threads
- First recommendation:
  - pre-produce a dedicated milestone video for each key mission checkpoint and publish within `30` minutes of the event
- Calendar preview count: `5`
- Internal note: public tweet data only; the skill suggested OAuth connection would add deeper funnel metrics such as link clicks and profile visits

### T3 TikTok `@khaby.lame`

- Followers: `160600000`
- Niche: `Comedy / Reaction / Skit`
- Audience persona: globally distributed Gen Z / Millennial audience responding to language-light physical comedy
- Engagement: `0.9%` (`below_average` for this follower tier)
- Benchmark context: mega-account TikTok ER is often around `1.5%–3%`; top posts here still spiked to `3.74%–4.81%`, indicating strong outliers over a weak average baseline
- Posting frequency: `1.0/week`
- Best content type: `Video`
- Best posting days: `Tuesday`, `Friday`
- Trend: `declining`
- Top-performing themes:
  - birthday/personal milestone
  - physical reaction comedy
  - everyday object absurdity
- Major content gaps:
  - no episodic series structure
  - no duet/stitch usage despite being core to historical account growth
  - little behind-the-scenes personality content
  - branded integrations underperforming the core comedy formula
- Top posts:
  - `VIDEO` `4.81%` ER: birthday locked-out gag
  - `VIDEO` `3.74%` ER: refreshment reaction gag
  - `VIDEO` `4.27%` ER: belt-fail everyday-object absurdity
- Growth opportunities:
  - revive duet/stitch format
  - episodic content series
  - personal / behind-the-scenes layer
  - reformat branded integrations
- First recommendation:
  - post a duet/stitch reacting to an overcomplicated life-hack video in the original silent reaction format
- Calendar preview count: `4`
- Internal note: public TikTok data was already considered the richest public data source among the three tested platforms

## Totals

- Tool/compute time: `265.737s`
- Estimated LLM overhead: `51.109949s`
- Skill/compute share: `83.8692%`
- LLM/overhead share: `16.1308%`

## Tokens And Cost

- Raw extractor reference: `python3 /home/ec2-user/Pikabot/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --json`
- Benchmark token accounting used rollout `token_count` deltas between `WALL_START` and `WALL_END`, because the latest cumulative extractor output includes earlier turns in this Codex session
- Input tokens: `1905892`
- Output tokens: `2919`
- Cached input tokens: `1900032`
- Cache write tokens: `null`
- Total tokens recorded in `result.json`: `3808843` (`input + output + cache_read`, matching the benchmark template convention)
- Estimated cost using `gpt-5.4` pricing (`$2.50/M` input, `$10.00/M` output): `$4.79392`

## Notes

- The skill needed `PIKABOT_STATE_DIR=/tmp` in this environment; otherwise it completed analysis but failed at the final `save_report()` step because the default `/data/.pikabot` location was not writable from the Codex sandbox.
- Instagram was the slowest case end-to-end, driven mostly by external fetch latency. X was the fastest because its fetch phase finished in about `6s`.
- Across all three cases, the fetch phase totaled about `47.2s`, while the skill's own LLM stages totaled about `218.1s`, so most of the execution time was in analysis generation rather than data retrieval.
- The reported engagement rates for `@natgeo` and `@NASA` were very low relative to follower counts, but the per-post outliers still aligned with the benchmark contexts produced by the skill.
