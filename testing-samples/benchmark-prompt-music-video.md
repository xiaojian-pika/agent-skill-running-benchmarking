# Benchmark: music-video

**Skill:** music-video
**Test input:** "APT." by ROSE ft. Bruno Mars — Apple Music 30s preview
**Audio:** ~30s mp3 via Apple Music search
**Engine:** Kling (default per SKILL.md) via `kling_via_fal` FAL fallback
**Avatar:** bot avatar (self-gen via Gemini)
**Expected output:** A ~30s 9:16 vertical music video mp4 with karaoke captions

Skill path: `/Users/rinko/nova3-agent-skills/music-video/`

---

## Claude Code Prompt

Start a new Claude Code session: `claude --model sonnet` (Sonnet 4.6). Send this prompt:

````
You are running a full end-to-end performance benchmark of the music-video skill on Claude Code. This is a self-benchmarking task — you will execute the entire music-video pipeline yourself and record all timing + token data.

First read these two files:
- /Users/rinko/agent-skill-running-benchmarking/templates/benchmark-run.json  (output format)
- /Users/rinko/agent-skill-running-benchmarking/templates/recording-guide.md  (how to fill fields)

Then read the skill spec:
- /Users/rinko/nova3-agent-skills/music-video/SKILL.md

All intake decisions are pre-determined (do NOT ask the user — just proceed):
- Song: "APT." by ROSE ft. Bruno Mars
- Lyrics (approx for 30s preview):
  ```
  [verse]
  You call me and I come running
  No one does it better than me
  [chorus]
  APT APT APT APT
  APT APT APT APT
  ```
- Audio source: Apple Music search (30s preview)
- Engine: Kling (use `kling_via_fal` from SKILL.md FAL AI Helpers section if direct Kling API returns 429/503/connection error)
- Avatar: bot avatar (self-gen via Gemini)
- Lipsync provider: LTX-2.3 (fal-ai/ltx-2.3/audio-to-video)

## Setup

```bash
WORK="/tmp/music-video"
mkdir -p $WORK/clips $WORK/keyframes
SKILLS="/Users/rinko/nova3-agent-skills"
```

## Steps

### 1. Clean + record wall start
```bash
rm -rf /tmp/music-video && mkdir -p /tmp/music-video/clips /tmp/music-video/keyframes
WALL_START=$(date +%s%N)
echo "WALL_START=$WALL_START"
echo "WALL_START_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

### 2. Asset acquisition — Apple Music search
```bash
T=$(date +%s%N)
python3 "$SKILLS/apple-music-reference/scripts/apple_music.py" \
  "APT ROSE Bruno Mars" /tmp/music-video/audio.m4a
echo "apple_music_search: $(( ($(date +%s%N) - T) / 1000000 ))ms"

T=$(date +%s%N)
ffmpeg -y -i /tmp/music-video/audio.m4a \
  -acodec libmp3lame -ar 44100 -ab 128k -ac 1 /tmp/music-video/audio.mp3
echo "convert_m4a_to_mp3: $(( ($(date +%s%N) - T) / 1000000 ))ms"

AUDIO_DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 /tmp/music-video/audio.mp3)
echo "Audio duration: ${AUDIO_DURATION}s"
```

### 3. Shot script generation (LLM call)
Time this phase: from LLM call start to shot_script.json written.

Generate the shot script using the LLM prompt in SKILL.md Step 3. For this 30s audio:
- Target 8-12 clips (15-20 clips/min × 0.5 min ≈ 8-10 clips)
- Clip durations: 2-4s each
- Shot types: mix of lipsync, character, empty, broll_instrument
- Engine: Kling (with kling_via_fal fallback) | Mood: upbeat K-pop | Genre: pop

Record the wall time for the LLM call and save output to /tmp/music-video/shot_script.json.

Validate:
```bash
T=$(date +%s%N)
python3 -c "
import json, sys
clips = json.load(open('/tmp/music-video/shot_script.json'))
total = sum(c['duration'] for c in clips)
print(f'{len(clips)} clips, total duration: {total:.1f}s')
for c in clips:
  assert all(k in c for k in ['id','start','end','duration','type','scene_prompt']), f'Missing field in clip {c}'
print('shot_script.json OK')
"
echo "shot_script_validate: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

### 4. Character reference generation (Gemini image)
```bash
T=$(date +%s%N)
python3 "$SKILLS/gemini/scripts/generate-image-gemini.py" \
  --prompt "young Korean woman, dark shoulder-length hair, pink leather jacket, expressive face, bust shot portrait, facing camera directly, neutral expression, mouth slightly open, plain dark background, 9:16 vertical, photorealistic, single person only" \
  --filename /tmp/music-video/character_ref.jpg \
  --aspect-ratio 9:16 \
  --resolution 1K \
  --model light
echo "character_ref_gen: $(( ($(date +%s%N) - T) / 1000000 ))ms"
echo "character_ref size: $(du -k /tmp/music-video/character_ref.jpg | cut -f1)KB"
```

### 5. Keyframe generation (Gemini API, all clips)
```bash
T=$(date +%s%N)
python3 -c "
import sys, os, json
WORK = '/tmp/music-video'
SKILLS = '/Users/rinko/nova3-agent-skills'
sys.path.insert(0, f'{SKILLS}/music-video/scripts')
from keyframes import generate_keyframes

clips = json.load(open(f'{WORK}/shot_script.json'))
project = {
    'project_dir': WORK,
    'meta': {'orientation': 'portrait'},
    'story': {'tone': 'upbeat K-pop, vibrant neon color, energetic'},
    'characters': [{'id': 'char_01', 'description': 'young Korean woman, dark shoulder-length hair, pink leather jacket', 'image_path': f'{WORK}/character_ref.jpg'}],
    'scenes': [],
    'shots': [
        {
            'id': c['id'],
            'scene_id': '',
            'character_ids': ['char_01'] if c['type'] in ('lipsync', 'character') else [],
            'keyframe_prompt': c['scene_prompt'],
            'script': {'action': c['scene_prompt'], 'camera_move': '', 'audio': ''},
            'shot_type': 'close_up' if c['type'] == 'lipsync' else 'medium_shot'
        }
        for c in clips
    ],
    'pipeline_status': {'plan': 'done'}
}
generate_keyframes(project_dir=WORK)
n = len([f for f in os.listdir(f'{WORK}/keyframes') if f.endswith('.jpg')])
print(f'keyframes generated: {n}')
"
echo "keyframe_gen: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

### 6. Parallel video generation (Kling/kling_via_fal + LTX lipsync)

Assign clips to batches (per SKILL.md Step 3 batch assignment), then spawn worker subagents in parallel — one per batch.

For each clip:
- **lipsync** → extract audio segment, then `lipsync_via_fal` (LTX-2.3)
- **character** → Kling direct API (`kling.py image-to-video`) → fallback `kling_via_fal` on 429/503
- **empty / broll_instrument** → Kling direct API from keyframe → fallback `kling_via_fal`

Workers save outputs to `/tmp/music-video/clips/clip_{id}.mp4`.

Record:
- `T_VIDEO_GEN_START=$(date +%s%N)` before spawning workers
- `T_VIDEO_GEN_END=$(date +%s%N)` after all workers finish
- For each clip: log individual clip duration

### 7. Assembly
```bash
T=$(date +%s%N)
# Normalize all clips
for f in /tmp/music-video/clips/clip_*.mp4; do
  id=$(basename $f .mp4 | sed 's/clip_//')
  ffmpeg -y -i "$f" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1" \
    -c:v libx264 -preset fast -crf 23 -an \
    /tmp/music-video/clips/norm_${id}.mp4
done

# Concat
ls /tmp/music-video/clips/norm_*.mp4 | sort \
  | awk '{print "file \47" $0 "\47"}' > /tmp/music-video/concat_norm.txt
ffmpeg -y -f concat -safe 0 -i /tmp/music-video/concat_norm.txt \
  -c:v copy /tmp/music-video/raw_concat.mp4

# Mix audio
ffmpeg -y \
  -i /tmp/music-video/raw_concat.mp4 \
  -i /tmp/music-video/audio.mp3 \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest \
  /tmp/music-video/raw_audio.mp4
echo "assembly: $(( ($(date +%s%N) - T) / 1000000 ))ms"
echo "raw_audio size: $(du -k /tmp/music-video/raw_audio.mp4 | cut -f1)KB"
```

### 8. Captions
```bash
T=$(date +%s%N)
python3 "$SKILLS/video-captions/scripts/caption_video.py" \
  /tmp/music-video/raw_audio.mp4 \
  /tmp/music-video/final.mp4 \
  --style karaoke --no-vad
echo "captions: $(( ($(date +%s%N) - T) / 1000000 ))ms"
echo "final size: $(du -k /tmp/music-video/final.mp4 | cut -f1)KB"
```

### 9. Upload + deliver
```bash
T=$(date +%s%N)
python3 -c "
import sys
sys.path.insert(0, '/Users/rinko/nova3-agent-skills')
from nova3_common.cdn import upload_to_cdn
from nova3_common.config import get_proxy_config
base_url, api_key = get_proxy_config()
url = upload_to_cdn('/tmp/music-video/final.mp4', base_url, api_key)
print(f'CDN URL: {url}')
"
echo "upload: $(( ($(date +%s%N) - T) / 1000000 ))ms"
```

### 10. Record wall end
```bash
WALL_END=$(date +%s%N)
echo "WALL_END=$WALL_END"
echo "WALL_END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
```

### 11. Token extraction
```bash
python3 /Users/rinko/agent-skill-running-benchmarking/tools/extract-cc-tokens.py \
  --latest \
  --after <WALL_START_ISO> \
  --before <WALL_END_ISO> \
  --json
```

## Token tracking

After all steps complete, extract token usage with:
```bash
python3 /Users/rinko/agent-skill-running-benchmarking/tools/extract-cc-tokens.py \
  --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Note: with Claude caching, most input tokens appear in `cache_read_tokens`. Use `effective_input_tokens` (= input + cache_read + cache_write) for real cost. Subagent tokens (coordinator + workers) are included in the session totals automatically.

## Output

Fill in the benchmark-run.json template and save to:
`/Users/rinko/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_music-video_run1/result.json`

Also write a brief `report.md` in the same directory.

Key values:
- `platform.name`: `"claudecode"`
- `platform.runtime`: `"local Mac"`
- `platform.llm_model`: your model name (e.g. `"Claude Sonnet 4.6"`)
- `phases.install`: all null (skill pre-installed, no CMS fetch)
- `phases.asset_acquisition.download_s`: apple_music_search + convert_m4a time
- `phases.execution.steps`:
  - `shot_script_gen`: LLM shot script generation time
  - `character_ref_gen`: Gemini character reference image time
  - `keyframe_gen`: Gemini keyframe generation time (all clips)
  - `parallel_video_gen`: total wall time for all workers (longest single phase)
  - `assembly`: ffmpeg normalize + concat + audio mix time
  - `captions`: caption_video.py time
- `phases.delivery.upload_s`: CDN upload time
- `tokens`: fill from extract-cc-tokens.py output (includes all subagents)
- `cost`: calculate from tokens × pricing (Sonnet 4.6: $3/$15/$3.75/$0.30 per million)
- `totals.wall_total_s`: end-to-end wall clock
- `totals.llm_overhead_s`: wall_total - all tool_call times
- `totals.llm_pct`: llm_overhead / wall_total × 100

Validate:
```bash
python3 /Users/rinko/agent-skill-running-benchmarking/tools/validate-run.py \
  /Users/rinko/agent-skill-running-benchmarking/runs/<dir>/
```

Do NOT skip any steps. Record all raw timing numbers.
````

---

## Timing notes for music-video

Unlike script-based skills, music-video's primary execution is LLM-driven orchestration with external API calls:

| Phase | Expected time | Type |
|-------|--------------|------|
| Apple Music search | 5-15s | API call |
| Shot script gen (LLM) | 10-30s | LLM |
| Character ref gen (Gemini) | 10-20s | API call |
| Keyframe gen (Gemini, 8-12 clips) | 60-120s | API calls |
| Parallel video gen (Kling/FAL, ~10 clips) | 30-90 min | API calls (parallel) |
| Assembly (ffmpeg) | 5-30s | CPU |
| Captions (Whisper + ffmpeg) | 15-60s | CPU |
| CDN upload | 5-30s | Network |

**Total expected: 60-120 min for 30s Apple Music preview with Kling engine (kling_via_fal ~10-15 min/clip)**

LLM overhead comes from:
- Coordinator subagent instructions + progress messages
- Worker subagent per-clip progress messages
- Shot script generation
- Keyframe generation orchestration

## Phases → execution.steps mapping

`execution.steps` records each sub-step as a breakdown of `skill_run_s`:
- `shot_script_gen` — LLM prompt → shot_script.json
- `character_ref_gen` — Gemini text-to-image
- `keyframe_gen` — Gemini keyframes for all clips
- `parallel_video_gen` — all workers combined wall time (longest step by far)
- `assembly` — ffmpeg normalize + concat + audio mix
- `captions` — caption_video.py (Whisper transcription + burn)

Note: `parallel_video_gen` is the aggregate. Individual clip times are in the worker logs, not in result.json (they're too granular for the benchmark format).
