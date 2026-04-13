# Benchmark Prompt: video-translation

> **Skill:** video-translation
> **Test input:** charli-daily-vlog.mp4 (720x1280, 67.8s, HEVC+AAC, 4.9MB)
> **Test input URL:** https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4
> **Expected output:** Spanish-dubbed mp4 with cloned speaker voice (no lip sync)
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the video-translation skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Translate this video to Spanish (no lip sync):
https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4

Use `--target-lang es --no-lip-sync`.

## Steps

1. Clean: `rm -f /tmp/bench_vt_* 2>/dev/null`
3. Record wall start: `echo "WALL_START=$(date +%s%N)"`
4. Install skill "video-translation" from Pika Staging Skill Hub. Time each sub-step:
   a. GET `https://skills-cms.pika-labs.app/api/hub/install?id=video-translation` → response has `bundleUrl` and `version`
   b. If `/data/.pikabot/workspace/skills/video-translation/SKILL.md` exists, remove the old folder first (this is an upgrade)
   c. Download zip from `bundleUrl`, extract to `/data/.pikabot/workspace/skills/video-translation/` (SKILL.md must be at root — flatten if nested in subfolder)
   d. Create a subagent to start a new session. The installed skill will be available for use.
5. Download the test video. Time it.
6. Run each stage individually and time it:
   - `ffprobe` (probe)
   - Full skill run: `python3 $PIKABOT_SKILLS_DIR/video-translation/scripts/translate_video.py <input> <output> --target-lang es --no-lip-sync`
7. Upload output to CDN using `pika-upload-file`. Time it.
8. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`


## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- LLM overhead = WALL_TOTAL - sum of all tool call times
- Do NOT combine multiple steps in one tool call
- Do NOT skip any steps

## Token & cost tracking

After the benchmark completes, parse the session JSONL at `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter entries where `type="message"` and `role="assistant"` within the benchmark timestamp window. Sum `message.usage.{input, output, cacheRead, cacheWrite}`. Fill:
- tokens.input_tokens, tokens.output_tokens, tokens.cache_read_tokens, tokens.cache_write_tokens
- tokens.total_tokens = sum of all above
- cost.estimated_cost_usd = (input_tokens × input_price + output_tokens × output_price) / 1,000,000

Pricing (2026-04): Opus 4.6 = $15/$75 per M, Sonnet 4.6 = $3/$15 per M

## Output

IMPORTANT: You MUST explicitly reply to me when done. Do not finish silently.

1. Save the complete filled-in JSON to `/tmp/bench_vt_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input info
- task: name="video-translation", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases: all timing values in seconds (convert ms to s)
- phases.execution.steps: extract_audio, transcribe_waterfall, translate_gpt4o, voice_clone_elevenlabs, tts_eleven_v3, replace_audio_ffmpeg
- delivery: upload_s, output_size_kb, output_url
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct
- tokens and cost: from session JSONL parsing

Also include a brief text summary of observations after the JSON.

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session (e.g. `claude --model sonnet` for Sonnet). Send this prompt:

````
Run a full e2e performance benchmark of the video-translation skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/video-translation/
- Python: ~/.venvs/captions/bin/python (has requests installed)
- Env vars needed: PYTHONPATH=/home/mingzhi/code/nova3-agent-skills, PIKA_API_BASE_URL, PIKA_AGENT_API_KEY
- Use mingzhi's staging fallback: PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art, PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o
- No install step, no upload step

## Steps

1. Clean: `rm -f /tmp/bench_vt_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"` — note the nanosecond value
3. Download test video:
   ```bash
   T=$(date +%s%N); curl -sL -o /tmp/bench_vt_input.mp4 "https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4"; echo "download_video: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   ```
4. Probe video:
   ```bash
   T=$(date +%s%N); ffprobe -v quiet -print_format json -show_format -show_streams /tmp/bench_vt_input.mp4 > /tmp/bench_vt_probe.json; echo "probe_video: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   ```
5. Full skill run:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/video-translation/scripts/translate_video.py \
     /tmp/bench_vt_input.mp4 /tmp/bench_vt_output.mp4 \
     --target-lang es --no-lip-sync 2>/tmp/bench_vt_skill_log.txt
   echo "skill_run: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   echo "output_size: $(du -k /tmp/bench_vt_output.mp4 | cut -f1) KB"
   cat /tmp/bench_vt_skill_log.txt
   ```
6. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - <WALL_START_VALUE>) / 1000000 ))ms"` — substitute the nanosecond value from step 2

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Replace `<WALL_START_ISO>` and `<WALL_END_ISO>` with the ISO timestamps (or epoch ms) from your wall start/end steps. The `--after`/`--before` flags isolate tokens to this benchmark task only (important if the session has other work).

This outputs input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, effective_input_tokens, total_tokens, and estimated_cost_usd. Note: with Claude caching, most input tokens appear in cache_read_tokens, not input_tokens. The effective_input_tokens field = input + cache_read + cache_write.

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_video-translation_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- platform.llm_model: your model name (e.g. "Claude Sonnet 4.6")
- phases.install: all null (no install)
- phases.delivery.upload_s: 0 (no upload)
- phases.execution.steps: extract_audio, transcribe_waterfall, translate_gpt4o, voice_clone_elevenlabs, tts_eleven_v3, replace_audio_ffmpeg
- tokens: fill from session stats
- cost: calculate from tokens × pricing. Include cache_read_price_per_million and cache_write_price_per_million (Sonnet 4.6: 0.30/3.75, GPT-5.4: 1.25/0)
- totals: wall_total_s, tool_calls_s, llm_overhead_s (wall - tools), llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Managed Claude Agent Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the video-translation skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/code/internal-prototyping/keys/.env` (the `ANTHROPIC_API_KEY` value)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `agent_011CZuSY9i9xpGSLRZ8HGFYF` (pika-video-translator)
- Environment ID: `env_01DFeEoMP4TH1q55w725r3ys` (pika-media-env, has ffmpeg + requests)
- The agent's system prompt has PIKA_API_BASE_URL and PIKA_AGENT_API_KEY in its ENVIRONMENT SETUP block
- **Fair comparison:** Other platforms (Claude Code, Codex) have dependencies pre-installed. Do NOT count dependency install or environment setup time in the benchmark. If the container is cold, pre-warm it in a throwaway session before starting the timed run.

## Steps

1. Clean: `rm -f /tmp/bench_mca_* 2>/dev/null`

2. Source the API key, record wall start, and create a session:
   ```bash
   export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/code/internal-prototyping/keys/.env | cut -d= -f2)
   AGENT_ID="agent_011CZuSY9i9xpGSLRZ8HGFYF"
   ENV_ID="env_01DFeEoMP4TH1q55w725r3ys"
   WALL_START=$(date +%s%N)
   echo "WALL_START=$WALL_START"
   SESSION=$(curl -sS https://api.anthropic.com/v1/sessions \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d "{
       \"agent\": \"$AGENT_ID\",
       \"environment_id\": \"$ENV_ID\",
       \"title\": \"Benchmark: video-translation $(date +%Y-%m-%d_%H%M)\"
     }")
   SESSION_ID=$(echo "$SESSION" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])")
   echo "Session: $SESSION_ID"
   ```

3. Send the task message. **Important:** the task message tells the agent to use `nohup` for the translation script (bash tool has a 295s timeout; the full pipeline — Whisper + GPT-4o + ElevenLabs clone + TTS + ffmpeg — can exceed this) and to suppress ffmpeg stderr:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{
       "events": [{
         "type": "user.message",
         "content": [{"type": "text", "text": "Translate this video to Spanish (no lip sync):\nhttps://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4\n\nPrepend your ENVIRONMENT SETUP exports (PIKA_AGENT_API_KEY, PIKA_API_BASE_URL, PYTHONPATH, nova3_common symlink) to every bash command that runs Python scripts.\n\nFollow these steps exactly, timing each one:\n\n## Step 1: Download\n```bash\nT_START=$(date +%s%N)\ncurl -sL \"https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4\" -o /mnt/session/outputs/input.mp4\nT_END=$(date +%s%N)\necho \"download_ms: $(( (T_END - T_START) / 1000000 ))\"\nls -lh /mnt/session/outputs/input.mp4\n```\n\n## Step 2: Run translation script\nIMPORTANT: The bash tool has a 295s timeout. The full pipeline (Whisper + GPT-4o + ElevenLabs voice clone + TTS + ffmpeg) can exceed this. You MUST use nohup + background + poll pattern:\n```bash\nnohup bash -c '\n# <your ENVIRONMENT SETUP exports here>\nT_START=$(date +%s%N)\npython /workspace/skills/video-translation/scripts/translate_video.py /mnt/session/outputs/input.mp4 /mnt/session/outputs/translated.mp4 --target-lang es --no-lip-sync 2>/mnt/session/outputs/ffmpeg.log\nT_END=$(date +%s%N)\necho \"translate_ms: $(( (T_END - T_START) / 1000000 ))\" > /mnt/session/outputs/timing.txt\necho \"output_size_kb: $(du -k /mnt/session/outputs/translated.mp4 | cut -f1)\" >> /mnt/session/outputs/timing.txt\necho \"DONE\" >> /mnt/session/outputs/timing.txt\n' > /mnt/session/outputs/translate_stdout.log 2>&1 &\necho \"PID: $!\"\n```\nThen poll every 10s:\n```bash\nwhile ! grep -q DONE /mnt/session/outputs/timing.txt 2>/dev/null; do sleep 10; done\ncat /mnt/session/outputs/timing.txt\ncat /mnt/session/outputs/translate_stdout.log\n```\nRedirect ffmpeg stderr to a file (2>/mnt/session/outputs/ffmpeg.log) — do NOT let it print to stdout, it bloats your context with hundreds of lines.\n\n## Step 3: Upload to CDN\nUse your ENVIRONMENT SETUP exports, then:\n```bash\nT_START=$(date +%s%N)\npython3 -c \"\nimport sys; sys.path.insert(0, '/workspace/skills')\nfrom nova3_common.cdn import upload_to_cdn\nfrom nova3_common.config import get_proxy_config\nbase_url, api_key = get_proxy_config()\nurl = upload_to_cdn('/mnt/session/outputs/translated.mp4', base_url, api_key)\nprint(f'CDN_URL: {url}')\n\"\nT_END=$(date +%s%N)\necho \"upload_ms: $(( (T_END - T_START) / 1000000 ))\"\n```\n\nReport all timing values and the CDN URL."}]
       }]
     }'
   ```

4. Poll session status every 5s until `status` is `idle` or `terminated` (timeout after 10 min):
   ```bash
   POLL_START=$(date +%s)
   while true; do
     STATUS=$(curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -H "anthropic-beta: managed-agents-2026-04-01")
     STATE=$(echo "$STATUS" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['status'])")
     ACTIVE=$(echo "$STATUS" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('stats',{}).get('active_seconds',0))")
     echo "$(date +%T) status=$STATE active=${ACTIVE}s"
     if [ "$STATE" = "idle" ] || [ "$STATE" = "terminated" ]; then break; fi
     if [ $(( $(date +%s) - POLL_START )) -gt 600 ]; then echo "TIMEOUT after 10min"; break; fi
     sleep 5
   done
   ```

5. Record wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

6. Fetch final session metadata (usage + stats + active_seconds):
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_session.json | python3 -m json.tool
   ```

7. Fetch all session events (for timing extraction):
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_events.json \
     | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(f'Events: {len(d.get(\"data\",[]))}'); [print(f'  {e[\"type\"]}') for e in d.get('data',[])]"
   ```

## Timing extraction

From `/tmp/bench_mca_events.json`, events have `processed_at` (ISO 8601) timestamps:
- **session.status_running** → T0 (container ready)
- **span.model_request_start / span.model_request_end** → LLM call durations; `model_request_end` has `model_usage`
- **agent.tool_use** → tool call start (matched to result via `id` field)
- **agent.tool_result** → tool call end (matched via `tool_use_id` field)
- **session.status_idle** → T_end

Run this script to extract all timing:
```bash
python3 -c "
import json
from datetime import datetime

def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z','+00:00'))

with open('/tmp/bench_mca_events.json') as f:
    events = json.loads(f.read())['data']

t0 = parse_ts([e for e in events if e['type']=='session.status_running'][0]['processed_at'])
t_end = parse_ts([e for e in events if e['type']=='session.status_idle'][0]['processed_at'])

# Tool call pairs (match tool_use.id → tool_result.tool_use_id)
pending = {}
tool_total = 0
for e in events:
    if e['type'] == 'agent.tool_use':
        pending[e['id']] = {'name': e.get('name',''), 'start': e['processed_at'],
                            'input': str(e.get('input',{}).get('command',''))[:120] or str(e.get('input',{}).get('file_path',''))[:120]}
    elif e['type'] == 'agent.tool_result' and e.get('tool_use_id') in pending:
        tc = pending.pop(e['tool_use_id'])
        dur = (parse_ts(e['processed_at']) - parse_ts(tc['start'])).total_seconds()
        tool_total += dur
        err = ' [ERROR]' if e.get('is_error') else ''
        print(f'{tc[\"name\"]:6s} {dur:8.1f}s{err}  {tc[\"input\"]}')

# LLM call timing
llm_total = 0
mr_starts = []
for e in events:
    if e['type'] == 'span.model_request_start':
        mr_starts.append(e['processed_at'])
    elif e['type'] == 'span.model_request_end' and mr_starts:
        dur = (parse_ts(e['processed_at']) - parse_ts(mr_starts.pop(0))).total_seconds()
        llm_total += dur
        u = e.get('model_usage',{})
        print(f'  LLM  {dur:6.1f}s  in={u.get(\"input_tokens\",0)} out={u.get(\"output_tokens\",0)}')

wall = (t_end - t0).total_seconds()
print(f'\nwall_total_s:    {wall:.3f}')
print(f'tool_calls_s:    {tool_total:.3f}')
print(f'llm_overhead_s:  {wall - tool_total:.3f}')
print(f'llm_sum_s:       {llm_total:.3f}')
print(f'llm_pct:         {(wall - tool_total) / wall * 100:.1f}%')
print(f'skill_pct:       {tool_total / wall * 100:.1f}%')
"
```

## Token & cost tracking

From `/tmp/bench_mca_session.json`:
- `usage.input_tokens` → tokens.input_tokens
- `usage.output_tokens` → tokens.output_tokens
- `usage.cache_read_input_tokens` → tokens.cache_read_tokens
- `usage.cache_creation.ephemeral_5m_input_tokens` → tokens.cache_write_tokens
- cost = (input×$3 + output×$15 + cache_read×$0.30 + cache_write×$3.75) / 1,000,000

Extract with:
```bash
python3 -c "
import json
with open('/tmp/bench_mca_session.json') as f:
    s = json.loads(f.read())
u = s['usage']
inp = u['input_tokens']
out = u['output_tokens']
cr = u.get('cache_read_input_tokens', 0)
cw = (u.get('cache_creation') or {}).get('ephemeral_5m_input_tokens', 0)
total = inp + out + cr + cw
cost = (inp*3 + out*15 + cr*0.30 + cw*3.75) / 1_000_000
print(f'input_tokens:       {inp}')
print(f'output_tokens:      {out}')
print(f'cache_read_tokens:  {cr}')
print(f'cache_write_tokens: {cw}')
print(f'total_tokens:       {total}')
print(f'estimated_cost_usd: {cost:.4f}')
print(f'active_seconds:     {s[\"stats\"][\"active_seconds\"]}')
print(f'model:              {s[\"agent\"][\"model\"][\"id\"]}')
"
```

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_video-translation_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "managed-claude-agent"
- platform.runtime: "Anthropic managed container"
- platform.llm_model: from session metadata (e.g. "Claude Sonnet 4.6")
- phases.install: all null (environment has deps pre-loaded via init_script)
- phases.execution.steps: map tool calls by command content (curl=download, translate_video.py=execution, upload_to_cdn=delivery)
- phases.delivery: timed from tool call events when agent uploaded to CDN
- tokens: from session usage metadata
- cost: calculate from tokens x pricing
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Codex Prompt

Start a Codex session. Send this prompt:

````
Run a full e2e performance benchmark of the video-translation skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/video-translation/
- Python: ~/.venvs/captions/bin/python (has requests installed)
- Env vars needed: PYTHONPATH=/home/mingzhi/code/nova3-agent-skills, PIKA_API_BASE_URL, PIKA_AGENT_API_KEY
- Use mingzhi's staging fallback: PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art, PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o
- No install step, no upload step

## Steps

1. Clean: `rm -f /tmp/bench_vt_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"` — note the nanosecond value
3. Download test video:
   ```bash
   T=$(date +%s%N); curl -sL -o /tmp/bench_vt_input.mp4 "https://mellis-test-assets.s3.us-east-1.amazonaws.com/video-translation-tests/charli-daily-vlog.mp4"; echo "download_video: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   ```
4. Probe video:
   ```bash
   T=$(date +%s%N); ffprobe -v quiet -print_format json -show_format -show_streams /tmp/bench_vt_input.mp4 > /tmp/bench_vt_probe.json; echo "probe_video: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   ```
5. Full skill run:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/video-translation/scripts/translate_video.py \
     /tmp/bench_vt_input.mp4 /tmp/bench_vt_output.mp4 \
     --target-lang es --no-lip-sync 2>/tmp/bench_vt_skill_log.txt
   echo "skill_run: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   echo "output_size: $(du -k /tmp/bench_vt_output.mp4 | cut -f1) KB"
   cat /tmp/bench_vt_skill_log.txt
   ```
6. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - <WALL_START_VALUE>) / 1000000 ))ms"` — substitute the nanosecond value from step 2

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Replace `<WALL_START_ISO>` and `<WALL_END_ISO>` with the ISO timestamps (or epoch ms) from your wall start/end steps. The `--after`/`--before` flags compute a delta between token snapshots, isolating this task from others in the same session.

This outputs input_tokens, output_tokens, cache_read_tokens, total_tokens, and estimated_cost_usd.

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_video-translation_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "codex"
- platform.runtime: "Codex sandbox"
- platform.llm_model: your model name (e.g. "GPT-4o")
- phases.install: all null (no install)
- phases.delivery.upload_s: 0 (no upload)
- phases.execution.steps: extract_audio, transcribe_waterfall, translate_gpt4o, voice_clone_elevenlabs, tts_eleven_v3, replace_audio_ffmpeg
- tokens: fill from session stats if available, null otherwise
- cost: calculate from tokens × pricing. Include cache_read_price_per_million and cache_write_price_per_million (Sonnet 4.6: 0.30/3.75, GPT-5.4: 1.25/0)
- totals: wall_total_s, tool_calls_s, llm_overhead_s (wall - tools), llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **/tmp file disappearance:** /tmp files can disappear between separate tool calls (root cause unknown). Chain download + probe + skill run as a single bash command (&&) to avoid this, while capturing individual timings via T=$(date +%s%N) variables within the same call.

- **Clean caches before each run:** `rm -f /tmp/bench_vt_*`
- **Pipeline:** extract audio → transcribe (Whisper → Deepgram → Gemini waterfall) → GPT-4o translate → ElevenLabs voice clone + TTS → ffmpeg audio replace.
- **API-bound skill** — 5 of 6 sub-steps are network calls (Whisper, GPT-4o, ElevenLabs ×2).
- **TTS is the bottleneck** — ElevenLabs eleven_v3 typically takes 15-30s (50-70% of skill time).
- **Output size:** ~3-4MB (smaller than input due to TTS audio bitrate).
- **Voice clone cleanup:** Script auto-deletes cloned voice after translation.
- **Managed agent bash timeout:** 295s per tool call. The full translation pipeline (Whisper + GPT-4o + ElevenLabs clone + TTS + ffmpeg) can exceed this. Always use `nohup` + background + poll pattern for the translate step.
- **ffmpeg stderr:** Verbose output bloats LLM context. Always redirect with `2>/path/to/log` on managed agents.
- **API key:** Source from `~/code/internal-prototyping/keys/.env`. Check it's valid with a test call before starting the benchmark.

## Processing PikaBot Results

When PikaBot sends back the result JSON (as a CDN URL or pasted text):

1. **Download the JSON** (if CDN URL):
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_result.json
   ```

2. **Create the run directory and save**:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_video-translation_runN
   mkdir -p "$RUN_DIR"
   cp /tmp/pikabot_result.json "$RUN_DIR/result.json"
   ```

3. **Generate report.md** from the JSON:
   ```bash
   python3 -c "
   import json
   with open('$RUN_DIR/result.json') as f:
       d = json.load(f)
   t = d['totals']
   p = d['phases']
   tk = d['tokens']
   print(f'# video-translation Benchmark — pikabot / {d[\"platform\"][\"llm_model\"]}')
   print(f'')
   print(f'**Date:** {d[\"meta\"][\"date\"]}')
   print(f'**Platform:** pikabot on {d[\"platform\"][\"runtime\"]}')
   print(f'**Skill:** video-translation {d[\"task\"][\"version\"]}')
   print(f'')
   print(f'## Results')
   print(f'')
   print(f'| Metric | Value |')
   print(f'|--------|-------|')
   print(f'| Wall total | **{t[\"wall_total_s\"]}s** |')
   print(f'| Tool calls | {t[\"tool_calls_s\"]}s ({t[\"skill_pct\"]:.0f}%) |')
   print(f'| LLM overhead | {t[\"llm_overhead_s\"]}s ({t[\"llm_pct\"]:.0f}%) |')
   if p.get('delivery',{}).get('output_size_kb'):
       print(f'| Output size | {p[\"delivery\"][\"output_size_kb\"]} KB |')
   if tk.get('total_tokens'):
       print(f'| Total tokens | {tk[\"total_tokens\"]:,} |')
   if d.get('cost',{}).get('estimated_cost_usd'):
       print(f'| Estimated cost | \${d[\"cost\"][\"estimated_cost_usd\"]} |')
   print(f'')
   print(f'## Timing breakdown')
   print(f'')
   print(f'| Step | Time |')
   print(f'|------|------|')
   if p.get('install',{}).get('cms_fetch_s'):
       print(f'| cms_fetch | {p[\"install\"][\"cms_fetch_s\"]}s |')
   if p.get('install',{}).get('skill_install_s'):
       print(f'| skill_install | {p[\"install\"][\"skill_install_s\"]}s |')
   if p.get('asset_acquisition',{}).get('download_s'):
       print(f'| download_video | {p[\"asset_acquisition\"][\"download_s\"]}s |')
   if p.get('execution',{}).get('skill_run_s'):
       print(f'| skill_run | {p[\"execution\"][\"skill_run_s\"]}s |')
   for s in p.get('execution',{}).get('steps',[]):
       print(f'| — {s[\"name\"]} | {s[\"duration_s\"]}s |')
   if p.get('delivery',{}).get('upload_s'):
       print(f'| upload_output | {p[\"delivery\"][\"upload_s\"]}s |')
   print(f'')
   print(f'## Observations')
   print(f'')
   print(d.get('meta',{}).get('notes',''))
   " > "$RUN_DIR/report.md"
   ```

4. **Validate**:
   ```bash
   python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py "$RUN_DIR"
   ```
