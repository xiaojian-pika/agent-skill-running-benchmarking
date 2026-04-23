# Benchmark Prompt: short-ads

> **Skill:** short-ads
> **Test input:** Brand brief + 3 local image files (logo, product, character or functional description)
> **Expected output:** 30s landscape 16:9 MP4 (2×15s acts) with SeeDance-generated video, MiniMax BGM, ElevenLabs VO
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## Standard Test Brief

Use this brand brief as the test input. It exercises all pipeline stages:

```
Brand: FREITAG (Swiss upcycled bag brand)
Product: Sky blue tarp cube backpack
Logo: Logo_Freitag.png (white wordmark on black)
Product image: freitag-sky-blue-bag.webp
Character: Athletic female figure, sunny warm complexion, fitted grey outdoor jacket — no character reference image, describe functionally
Concept: "The City Gave It Back" — cargo truck tarp → workshop transformation → bag returned to city streets
Tagline: "The city gave it back."
Voice: Brian (English, deep resonant)
Tone: Urban-lyrical, contemplative, Swiss precision
```

This brief exercises:
- LLM: concept pitch → brand tone profile → 10-shot visual script → 2× Seedance prompt pairs (EN+ZH)
- SeeDance 2.0 r2v: 2× 15s parallel video generations (Act 1 + Act 2) via fal.ai
- MiniMax music-2.5: ~36s ambient electronic BGM
- ElevenLabs eleven_v3: short slogan VO (Brian voice)
- ffmpeg: concat + crop + eq + audio mix

---

## Claude Code Prompt

Start a new Claude Code session in the `nova3-agent-skills/short-ads/` directory. Send this prompt:

````
Run a full e2e performance benchmark of the short-ads skill. Read:
- ~/nova3-agent-skills/short-ads/SKILL.md (skill definition)
- ~/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/agent-skill-running-benchmarking/templates/recording-guide.md (field instructions)

Fill in the JSON template with actual measured values.

## Assets (already local)
- Logo: ~/Desktop/Logo_Freitag.png
- Product: ~/Desktop/000003899622_1-20240923161710.webp (sky blue tarp backpack)
- Character: no image — athletic female, sunny complexion, grey outdoor jacket

## Brand brief
- Brand: FREITAG
- Product: sky blue tarp cube backpack
- Concept: "The City Gave It Back" — truck tarp → workshop → bag back in city streets
- Tagline: "The city gave it back."
- Voice: Brian (ElevenLabs, ID: nPczCjzI2devNBz1zQrb)

## Steps — record WALL_START before step 1, WALL_END after step 7

```bash
WALL_START=$(date +%s%N)
echo "WALL_START_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

1. **LLM phase** (concept + tone profile + visual script + Seedance prompts)
   Time from first LLM call to prompt generation complete. This is pure LLM overhead.

2. **Video generation** (run Act 1 + Act 2 in parallel):
```bash
T=$(date +%s%N)
# [run seedance.py Act 1 in background]
# [run seedance.py Act 2 in background]
# [wait for both]
echo "seedance_wall: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

3. **ffmpeg concat**:
```bash
T=$(date +%s%N)
ffmpeg -y -f concat -safe 0 -i /tmp/[brand]/concat.txt -c:v libx264 -crf 18 -an /tmp/[brand]/video_noaudio.mp4
echo "ffmpeg_concat: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

4. **BGM** (MiniMax music-2.5):
```bash
T=$(date +%s%N)
# [MiniMax API call]
echo "bgm_minimax: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

5. **VO** (ElevenLabs eleven_v3):
```bash
T=$(date +%s%N)
# [ElevenLabs API call]
echo "vo_elevenlabs: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

6. **Final encode** (ffmpeg crop+eq+audio mix):
```bash
T=$(date +%s%N)
ffmpeg -y -i video_noaudio.mp4 -i bgm.mp3 -i vo.mp3 \
  -filter_complex "[0:v]crop=1200:675:40:22,scale=1280:720..." \
  /tmp/[brand]/final.mp4
echo "ffmpeg_encode: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

7. Record wall end:
```bash
WALL_END=$(date +%s%N)
echo "WALL_END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
```

## Token extraction

```bash
python3 ~/agent-skill-running-benchmarking/tools/extract-cc-tokens.py \
  --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Save result.json to:
  ~/agent-skill-running-benchmarking/runs/2026-04-23_claudecode_claude-sonnet-4-6_short-ads_run1/result.json

Key fields:
- meta.test_input.description: "Freitag sky-blue tarp backpack TVC from brand brief"
- task.name: "short-ads", task.version: "2.0.0"
- phases.execution.steps: llm_concept_script_prompts, seedance_act1, seedance_act2, ffmpeg_concat, bgm_minimax, vo_elevenlabs, ffmpeg_encode
- delivery.output_size_kb, delivery.output_url (local path)
- Note: acts run in parallel — wall time for video = max(act1, act2), not sum

Run `python3 ~/agent-skill-running-benchmarking/tools/validate-run.py runs/<dir>/` and fix any errors.
````

---

## PikaBot Prompt

Send this along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the short-ads skill.

## What to benchmark

Generate a 30s brand TVC for FREITAG using:
- Brand: FREITAG (Swiss upcycled bag brand)  
- Product: sky blue tarp cube backpack
- Concept: "The City Gave It Back" — truck tarp → workshop → returned to city streets
- Tagline: "The city gave it back."
- Voice: Brian (ElevenLabs deep resonant English)

## Steps

1. Record wall start
2. Install skill "short-ads" from Skill Hub. Time: cms_fetch, download+extract, subagent boot.
3. LLM phase: generate concept, tone profile, visual script, Seedance prompts. Time from first LLM call to prompt output.
4. Video: run seedance.py Act 1 + Act 2 in parallel. Time wall (parallel wall = max of two, not sum).
5. BGM: MiniMax music-2.5. Time API call.
6. VO: ElevenLabs eleven_v3 Brian. Time API call.
7. ffmpeg concat + final encode. Time each.
8. Record wall end.

## Output

Key fields:
- phases.execution.steps: llm_concept_script_prompts, seedance_act1, seedance_act2, ffmpeg_concat, bgm_minimax, vo_elevenlabs, ffmpeg_encode
- Note acts are parallel — record both durations, use wall time for total
```

---

## Notes on Timing Breakdown

| Step | API/Tool | Typical duration |
|------|----------|-----------------|
| `llm_concept_script_prompts` | Claude (LLM only) | 180–360s |
| `seedance_act1` | fal.ai SeeDance 2.0 r2v | 180–360s |
| `seedance_act2` | fal.ai SeeDance 2.0 r2v (parallel) | 180–360s |
| `seedance_wall` | max(act1, act2) | 180–360s |
| `ffmpeg_concat` | local ffmpeg | 5–15s |
| `bgm_minimax` | MiniMax music-2.5 | 60–120s |
| `vo_elevenlabs` | ElevenLabs eleven_v3 | 3–10s |
| `ffmpeg_encode` | local ffmpeg | 15–45s |

**Important:** Act 1 and Act 2 run in parallel. Record both individual durations AND the wall time (= max of the two). The LLM phase (concept → script → prompts) is pure Claude overhead with no external API calls.
