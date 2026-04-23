# Benchmark Prompt: short-film

> **Skill:** short-film
> **Test input:** Creative brief only (no video input — the skill generates all assets from scratch)
> **Expected output:** ~60s short film MP4 (portrait 9:16 or landscape 16:9) with Kling-generated video, background music, and optional lipsync, uploaded to CDN
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## Standard Test Brief

Use this creative brief as the test input. It's designed to exercise all pipeline stages:

```
1. Genre: Horror / psychological thriller
2. Orientation: Portrait (9:16)
3. Protagonist: Ji-yeon, 22-year-old Korean exchange student, short hair, thin-frame glasses, holds an old film camera, scared young female voice
4. Setting: East Coast US university campus, abandoned library, present day
5. Style: Cold noir, high contrast black and white with occasional amber highlights
6. Plot: Ji-yeon sneaks into the abandoned library at night to photograph it. She hears breathing behind a shelf, turns to find a pale girl in a white dress. The ghost says "You are not the first person to come to me."
```

This brief exercises:
- Character with visual traits → Gemini portrait generation
- Location + atmosphere → Gemini scene image generation
- 12-shot ~60s plan → 4–5 Kling multi-shot batches
- Dialogue line → MiniMax TTS + fal lipsync (or sfx_hint fallback)

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the short-film skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Generate a ~60s short horror film using this creative brief:
- Genre: Horror / psychological thriller
- Orientation: Portrait (9:16)
- Protagonist: Ji-yeon, 22-year-old Korean exchange student, short hair, thin-frame glasses, holds an old film camera
- Setting: East Coast US university, abandoned library
- Style: Cold noir, high contrast
- Plot: Ji-yeon sneaks into abandoned library at night. Discovers a ghost of a missing student who says: "You are not the first person to come to me."
- Music: Horror/suspense underscore, SFX-driven, lower volume than voices

## Steps

1. Record wall start: `echo "WALL_START=$(date +%s%N)"`
2. Install skill "short-film" from Pika Staging Skill Hub. Time each sub-step:
   a. GET `https://skills-cms.pika-labs.app/api/hub/install?id=short-film` → get `bundleUrl` and `version`
   b. Download + extract to `/data/.pikabot/workspace/skills/short-film/`
   c. Create a subagent to start a new session
3. Run each stage individually and time it:
   - Stage 0 (init): `python3 $PIKABOT_SKILLS_DIR/short-film/scripts/init.py --base-dir /tmp/short-film-bench`
   - Stage 1 (plan): Main agent writes story plan JSON directly using write_plan() function
   - Stage 2 (assets): `python3 $PIKABOT_SKILLS_DIR/short-film/scripts/assets.py --project-dir /tmp/short-film-bench/film_*`
   - Stage 3 (keyframes): `python3 $PIKABOT_SKILLS_DIR/short-film/scripts/keyframes.py --project-dir /tmp/short-film-bench/film_*`
   - Stage 4 (video): `python3 $PIKABOT_SKILLS_DIR/short-film/scripts/video.py --project-dir /tmp/short-film-bench/film_*`
   - Stage 4.5 (lipsync+CDN): `python3 $PIKABOT_SKILLS_DIR/short-film/scripts/lipsync.py --project-dir /tmp/short-film-bench/film_*`
4. Upload final output to CDN using `pika-upload-file`. Time it.
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`

## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- LLM overhead = WALL_TOTAL - sum of all tool call times
- Do NOT combine multiple steps in one tool call

## Token & cost tracking

After the benchmark completes, parse the session JSONL at `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter entries where `type="message"` and `role="assistant"` within the benchmark timestamp window. Sum `message.usage.{input, output, cacheRead, cacheWrite}`.

Pricing (2026-04): Sonnet 4.6 = $3/$15 per M (cache write $3.75/M, cache read $0.30/M)

## Output

1. Save the complete filled-in JSON to `/tmp/bench_sf_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: CDN URL, wall_total_s, tool_calls_s, llm_pct, and observations

Key fields:
- meta: date, tester="pikabot", test_input.description="horror short film from 7-question brief"
- task: name="short-film", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.execution.steps: init, plan, assets_gemini, keyframes_gemini, video_kling, lipsync_cdn
- delivery: upload_s, output_size_kb, output_url
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the short-film skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/short-film/
- Python: use system python3
- Env vars needed: PYTHONPATH=/home/mingzhi/code/nova3-agent-skills, PIKA_API_BASE_URL, PIKA_AGENT_API_KEY

## What to benchmark

Run the full short-film pipeline with this creative brief:
- Genre: Horror / psychological thriller
- Orientation: Portrait (9:16)
- Protagonist: Ji-yeon, 22yo Korean exchange student, short hair, thin-frame glasses, old film camera
- Setting: East Coast US university, abandoned library
- Style: Cold noir, high contrast
- Plot: Ji-yeon enters abandoned library at night. Discovers ghost who says: "You are not the first person to come to me."
- Music: Horror/suspense underscore, SFX-driven

## Steps

Record wall_start with `date +%s%N` before step 1, wall_end after step 6.

1. Stage 0 — init:
   `python3 ~/code/nova3-agent-skills/short-film/scripts/init.py --base-dir /tmp/sf_bench --theme "horror thriller" --orientation portrait --protagonist "Ji-yeon, 22yo Korean student, thin glasses, old camera" --worldview "East Coast US university, abandoned library" --style "cold noir, high contrast"`

2. Stage 1 — plan: Write the story plan JSON using write_plan() and save to project.json. Time from write_plan() call to file write completion.

3. Stage 2 — assets:
   `python3 ~/code/nova3-agent-skills/short-film/scripts/assets.py --project-dir /tmp/sf_bench/film_*`

4. Stage 3 — keyframes:
   `python3 ~/code/nova3-agent-skills/short-film/scripts/keyframes.py --project-dir /tmp/sf_bench/film_*`

5. Stage 4 — video:
   `python3 ~/code/nova3-agent-skills/short-film/scripts/video.py --project-dir /tmp/sf_bench/film_*`

6. Stage 4.5 — lipsync+CDN:
   `python3 ~/code/nova3-agent-skills/short-film/scripts/lipsync.py --project-dir /tmp/sf_bench/film_*`

## Timing rules

Use `date +%s%N` to time each step in nanoseconds, convert to seconds. LLM overhead = wall_total - sum of all tool call times.

## Token extraction

After the run, use:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest \
  --after <wall_start_iso> --before <wall_end_iso> --json
```

Use effective_input_tokens (= input + cache_read + cache_write) for real input cost.

## Output

Save result.json to:
  ~/code/agent-skill-running-benchmarking/runs/2026-04-15_claudecode_claude-sonnet-4-6_short-film_run1/result.json

Key fields:
- meta.test_input.description: "horror short film from 7-question creative brief, portrait 9:16"
- task.name: "short-film"
- phases.execution.steps: init, plan, assets_gemini, keyframes_gemini, video_kling (with substeps: kling_submit, kling_poll_all_batches, kling_download_assemble), lipsync_cdn (tts, fal_lipsync, cdn_upload)
- delivery.output_url: CDN URL of final.mp4

Also run `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py runs/2026-04-15_claudecode_claude-sonnet-4-6_short-film_run1/` and fix any errors.
````

---

## Managed Claude Agent Prompt

Start a session using `run_session.py` from `nova3-agent-skills/short-film/agent/`. Required env vars:

```bash
export SHORT_FILM_AGENT_ID=agent_011Ca5DzAVnAckNg438cPSR1
export SHORT_FILM_ENV_ID=env_01C7HCQETarSF2XMLwzx2PGZ
export SKILLS_GITHUB_URL=https://github.com/xiaojian-pika/nova3-agent-skills
export SKILLS_GITHUB_TOKEN=<github-pat>
```

Send this prompt as the initial message:

````
Run a full end-to-end performance benchmark of the short-film skill. Record wall time and per-stage timing.

## Setup
```bash
export PYTHONPATH="${PIKABOT_SKILLS_DIR}:${PYTHONPATH}"
mkdir -p /tmp/short-film
WALL_START=$(date +%s%N)
echo "WALL_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Creative brief (use exactly — standard horror test brief)
1. Genre: Horror / psychological thriller
2. Orientation: Portrait (9:16)
3. Protagonist: Ji-yeon, 22-year-old Korean exchange student, short hair, thin-frame glasses, holds an old film camera
4. Setting: East Coast US university campus, abandoned library, present day
5. Style: Cold noir, high contrast black and white with occasional amber highlights
6. Plot: Ji-yeon sneaks into the abandoned library at night to photograph it. She hears breathing behind a shelf, turns to find a pale girl in a white dress. The ghost says "You are not the first person to come to me." (use sfx_hint for dialogue, not TTS)

## Run the pipeline

Time each stage with `T=$(date +%s%N)` before and `echo "stage_X: $(( ($(date +%s%N) - T) / 1000000 ))ms"` after.

**Stage 0 — init:**
```bash
T=$(date +%s%N)
python3 ${PIKABOT_SKILLS_DIR}/short-film/scripts/init.py \
  --base-dir /tmp/short-film \
  --theme "horror psychological thriller" \
  --orientation portrait \
  --protagonist "Ji-yeon, 22yo Korean exchange student, short hair, thin-frame glasses, old film camera" \
  --worldview "East Coast US university campus, abandoned library, present day" \
  --style "cold noir, high contrast black and white, occasional amber highlights"
echo "stage_0_init: $(( ($(date +%s%N) - T) / 1000000 ))ms"
PROJECT_DIR=$(ls -d /tmp/short-film/film_* | head -1)
echo "PROJECT_DIR=$PROJECT_DIR"
```

**Stage 1 — plan:** Write the story plan JSON using write_plan() with 12 shots covering the horror brief. Use sfx_hint (not dialogue field) for the ghost's line. Time from write_plan() call to file write.

**Stage 2 — assets:**
```bash
T=$(date +%s%N)
python3 ${PIKABOT_SKILLS_DIR}/short-film/scripts/assets.py --project-dir $PROJECT_DIR
echo "stage_2_assets: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

**Stage 2.5 — script preview:** Present the shot-by-shot script to the user and wait for confirmation before proceeding.

**Stage 3 — keyframes:**
```bash
T=$(date +%s%N)
python3 ${PIKABOT_SKILLS_DIR}/short-film/scripts/keyframes.py --project-dir $PROJECT_DIR
echo "stage_3_keyframes: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

**Stage 3.5 — keyframe review:** Show keyframe grids to the user and wait for confirmation.

**Stage 4 — video:** Spawn as subagent after Stage 3.5 confirmation.

**Stage 4.5 — lipsync+mix:**
```bash
T=$(date +%s%N)
python3 ${PIKABOT_SKILLS_DIR}/short-film/scripts/lipsync.py --project-dir $PROJECT_DIR
echo "stage_4_5_lipsync: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

**Wall end:**
```bash
WALL_END=$(date +%s%N)
echo "WALL_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
```

## After completion

Report:
- CDN URL of final.mp4
- Wall start/end ISO timestamps
- Per-stage durations
- Final project directory path

I will handle saving the benchmark result.json and report.md from here.
````

---

## Codex Prompt

(Same task, adapted for Codex environment. Note: Codex has no persistent workspace between steps — wrap all stages in a single script with timing instrumentation.)

---

## Notes on Timing Breakdown

The short-film skill has these distinct API-heavy phases — record each separately:

| Step | API | Typical duration |
|------|-----|-----------------|
| `assets_gemini` | Gemini flash image preview × (chars + scenes) | 60–180s (parallel) |
| `keyframes_gemini` | Gemini flash image preview × shots | 120–360s (sequential or parallel) |
| `kling_submit` | Kling v3 omni multi-shot API (4–5 batches) | 10–30s |
| `kling_poll_all_batches` | Kling polling loop (all batches concurrent) | 180–600s |
| `kling_download_assemble` | Download + ffmpeg concat | 30–120s |
| `tts_minimax` | MiniMax speech-2.8-hd (per dialogue shot) | 5–30s/shot |
| `fal_lipsync` | fal-ai/sync-lipsync/v2 (per dialogue shot) | 120–300s/shot |
| `cdn_upload` | Upload final.mp4 | 10–60s |

**Important:** In abbreviated runs (reusing existing assets/keyframes), `assets_gemini` and `keyframes_gemini` will be near 0. Note this clearly in `meta.notes`.
