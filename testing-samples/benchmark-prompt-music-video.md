# Benchmark Prompt: music-video

> **Skill:** music-video
> **Test input:** 30-second Apple Music preview (Abracadabra — Lady Gaga)
> **Test input URL:** Apple Music search API via `apple-music-reference` skill
> **Expected output:** ~30s 9:16 music video (5-8 clips, karaoke captions, fal kling + ltx-2.3 lipsync)
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## Environment Prerequisites

The music-video skill uses **fal.ai** directly for clip generation and lipsync — it does NOT go through the Pika proxy for these calls.

**Required before running:**
- `FAL_KEY` — fal.ai API key. Set in environment or `~/.claude/settings.json` (Claude Code).
  Without this, clip generation (Steps 5a/5b/5c) will fail.
- `PIKA_AGENT_API_KEY` + `PIKA_API_BASE_URL` — for audio fetch, CDN upload, and Gemini keyframes.
- `PIKABOT_SKILLS_DIR` — root of nova3-agent-skills (e.g. `/app/skills` on PikaBot, `~/code/nova3-agent-skills` on devbox).
- `ffmpeg`, `ffprobe` — for audio/video processing.

```bash
# PikaBot: PIKA_* are auto-set. Set FAL_KEY via skill config or env.
# Devbox: source from ~/.claude/settings.json or keys/.env
export FAL_KEY=<your_fal_key>
export PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art   # staging
export PIKA_AGENT_API_KEY=<your_agent_key>
export PIKABOT_SKILLS_DIR=~/code/nova3-agent-skills
```

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the music-video skill. I've sent you the JSON template and recording guide — fill in measured values.

## What to benchmark

Generate a short music video:
- Audio: Lady Gaga "Abracadabra" (30s Apple Music preview via apple-music-reference)
- Engine: fal kling (fal-ai/kling-video/o3/pro/reference-to-video)
- Lipsync: ltx-2.3 (fal-ai/ltx-2.3/audio-to-video)
- Target: ~5-8 clips, 9:16, with karaoke captions

## Steps (time each individually)

1. Clean: `rm -rf /tmp/music-video /tmp/bench_mv_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s)"`

3. **Install check** — confirm music-video skill is installed:
   `ls /app/skills/music-video/SKILL.md && echo OK || echo MISSING`
   If missing: note as install failure. Skip to reporting.

4. **Audio acquisition** (time it):
   ```bash
   T=$(date +%s)
   mkdir -p /tmp/music-video/clips
   python3 $PIKABOT_SKILLS_DIR/apple-music-reference/scripts/apple_music.py \
     "abracadabra lady gaga" /tmp/music-video/audio_raw.m4a
   ffmpeg -y -i /tmp/music-video/audio_raw.m4a -acodec libmp3lame -ar 44100 -ab 128k -ac 1 /tmp/music-video/audio.mp3
   AUDIO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 /tmp/music-video/audio.mp3)
   echo "audio_acquisition_s: $(( $(date +%s) - T ))  duration=${AUDIO_DUR}s"
   ```

5. **Shot script generation** (time the LLM call):
   Generate a shot script for the 30s audio. Use this system:
   - Abracadabra lyrics: "Abracadabra, let me see it / Abracadabra, just believe it / Abracadabra, you can feel it / Abracadabra, abra-ca-da" (chorus × 2, with verse/outro padding)
   - Song mood: dark pop, theatrical, mystical
   - Generate 6-8 clips covering ~30s
   - Types: mix of lipsync + character + empty
   Save to `/tmp/music-video/shot_script.json`
   ```bash
   echo "shot_script_generation_s: $(( $(date +%s) - T ))"
   ```

6. **Keyframe generation** (time it):
   ```python
   import sys, os, json, time
   sys.path.insert(0, f"{os.environ['PIKABOT_SKILLS_DIR']}/music-video/scripts")
   from keyframes import generate_keyframes
   WORK = "/tmp/music-video"
   clips = json.load(open(f"{WORK}/shot_script.json"))
   project = {
       "project_dir": WORK,
       "meta": {"orientation": "portrait"},
       "story": {"tone": "dark pop, theatrical, mystical, neon, high contrast"},
       "characters": [{"id": "char_01", "description": "gothic woman, dark hair, dramatic makeup, mystical", "image_path": None}],
       "scenes": [],
       "shots": [{"id": c["id"], "scene_id": "", "character_ids": ["char_01"] if c["type"] in ("lipsync","character") else [], "keyframe_prompt": c["scene_prompt"], "script": {"action": c["scene_prompt"], "camera_move": "", "audio": ""}, "shot_type": "close_up" if c["type"] == "lipsync" else "medium_shot"} for c in clips],
       "pipeline_status": {"plan": "done"}
   }
   t0 = time.time()
   generate_keyframes(project_dir=WORK)
   print(f"keyframe_generation_s: {time.time()-t0:.1f}")
   ```

7. **Clip generation** (time it — expect FAL_KEY required):
   ```bash
   T=$(date +%s)
   # Check FAL_KEY
   [ -z "$FAL_KEY" ] && echo "BLOCKED: FAL_KEY not set — clip generation requires fal.ai direct access" && exit 0
   ```
   If FAL_KEY available, run each clip type:
   - Lipsync clips: `lipsync_via_fal()` with ltx-2.3
   - Character clips: `kling_via_fal()` with fal kling
   - Empty clips: `kling_via_fal()` with fal kling
   Time each clip individually.

8. **Assembly** (time it — only if clips were generated):
   Normalize + concat + audio mix + captions.
   `ffmpeg` concat → `caption_video.py --style karaoke`

9. **Upload** (time it):
   Upload final.mp4 using `pika-upload-file`. Record CDN URL.

10. Record wall end: `WALL_END=$(date +%s); echo "WALL_TOTAL: $(( WALL_END - WALL_START ))s"`

## Timing rules

- Time EVERY step. LLM overhead = WALL_TOTAL − sum of all tool call times.
- If FAL_KEY missing: record phases through keyframe generation, mark clip_generation as "blocked".

## Token & cost tracking

Parse `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter by benchmark timestamps. Sum `message.usage.{input, output, cacheRead, cacheWrite}`.

## Output

Save result JSON to `runs/YYYY-MM-DD_pikabot_claude-sonnet-4-6_music-video_runN/result.json`.
Write `report.md` in the same directory.

Key fields:
- task.name: "music-video"
- task.version: "feat/music-video@{commit_sha}"
- phases.execution.steps: audio_acquisition, shot_script_generation, keyframe_generation, clip_generation (per clip), assembly, captions
- notes: FAL_KEY availability, which fallbacks triggered
```

---

## Claude Code Prompt

```
Run a full e2e performance benchmark of the music-video skill.

Setup:
- Skill: ~/code/nova3-agent-skills/music-video/
- PIKABOT_SKILLS_DIR=~/code/nova3-agent-skills
- FAL_KEY=<from ~/.claude/settings.json or keys/.env>
- PIKA_API_BASE_URL, PIKA_AGENT_API_KEY from staging env

Follow the same steps as the PikaBot prompt above.
Save results to ~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_music-video_runN/
```

---

## Key Observations

### FAL_KEY Dependency
music-video clips are generated via direct fal.ai API calls (not Pika proxy). `FAL_KEY` must be set in the agent's environment. Without it, steps 5a/5b/5c fail. Phases 1-4 (audio, shot script, keyframes) run independently of FAL_KEY.

### Phase Timing Profile (expected)
| Phase | Est. Time |
|-------|-----------|
| audio_acquisition | 2-5s |
| shot_script_generation (LLM) | 5-15s |
| keyframe_generation (Gemini) | 10-30s |
| clip_generation (fal kling, 6 clips) | ~8-12 min |
| lipsync_per_clip (ltx-2.3, 2 clips) | ~3-5 min each |
| assembly + captions | ~30-60s |
| **total** | **~20-30 min** |

### LLM Overhead (PikaBot)
PikaBot's 106K system prompt dominates LLM cost. Expect 50-70% LLM overhead for this skill due to coordinator + worker subagent spawning.

### Notes
- Apple Music returns 30s preview only — use to keep benchmark short and cheap.
- Keyframe generation uses Gemini 2.0 Flash via pika proxy — fast and cheap.
- fal kling `o3/pro/reference-to-video` is the primary video engine.
- ltx-2.3 `fal-ai/ltx-2.3/audio-to-video` is the lipsync engine (single-step image+audio→video).
- Character consistency enforced via `character_ref.jpg` passed to all workers.
