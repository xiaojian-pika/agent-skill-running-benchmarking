# Benchmark Prompt: long-to-short-video

> **Skill:** long-to-short-video
> **Test URL:** https://www.youtube.com/watch?v=UNP03fDSj1U (Matt Cutts — "Try Something New for 30 Days", 3m27s)
> **Test cases:** T1 fresh 3-clip tiktok, T2 cache-hit rerun, T3 hormozi style fresh, T4 5-clip fresh
> **Expected output:** 3-5 short MP4 clips with captions, virality scores, CDN URLs
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the long-to-short-video skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Test video: https://www.youtube.com/watch?v=UNP03fDSj1U (Matt Cutts "Try Something New for 30 Days", 3m27s)

Run 4 test cases in order:
- T1: `--input <URL> --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev`  (fresh run)
- T2: same command, same `--out /tmp/lts_t1`  (cache hit — S1 download + face timeline + transcript should be skipped)
- T3: `--input <URL> --num-clips 3 --style hormozi --out /tmp/lts_t3 --dev`  (fresh run, new --out dir)
- T4: `--input <URL> --num-clips 5 --style tiktok --out /tmp/lts_t4 --dev`  (fresh run, 5 clips)

## Steps

1. Clean: `rm -rf /tmp/lts_t1 /tmp/lts_t3 /tmp/lts_t4 /tmp/bench_ltsv_skill.zip 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"`
3. Install skill "long-to-short-video" from Pika Staging Skill Hub (CMS). Time each sub-step (cms_fetch, skill_install, subagent_start).
4. Run T1 → T2 → T3 → T4 in sequence. Time each one individually. Always use `--dev` for verbose stderr timing.
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`

## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- Capture full stderr for each run (LTSV logs per-stage timing to stderr with `--dev`)
- Sub-stage timing comes from stderr markers:
  - `S1 got download URL in Xs` → Apify API; `S1 ✅ downloaded XMB in Xs` → file download
  - `S1 ✅ Video cache hit` → T2 download cache hit
  - `S2 ✅ Transcribed ... in Xs` → Whisper time
  - `S3 ✅ Selected N clips ... in Xs` → LLM clip selection
  - `S5 Face trajectory` → OpenCV face detection (infer from elapsed)
  - `S7 ✅ Clip N ready` → CDN upload per clip
- LLM overhead = WALL_TOTAL - sum of all tool call times
- Do NOT combine multiple steps in one tool call

## Token & cost tracking

After the benchmark completes, parse the session JSONL at `/data/.pikabot/agents/{agent_id}/sessions/{sessionId}.jsonl`. Filter entries where `type="message"` and `role="assistant"` within the benchmark timestamp window. Sum `message.usage.{input, output, cacheRead, cacheWrite}`. Fill:
- tokens.input_tokens, tokens.output_tokens, tokens.cache_read_tokens, tokens.cache_write_tokens
- tokens.total_tokens = sum of all above
- cost.estimated_cost_usd = (input_tokens × input_price + output_tokens × output_price) / 1,000,000

Pricing (2026-04): Opus 4.6 = $15/$75 per M, Sonnet 4.6 = $3/$15 per M

## Output

IMPORTANT: You MUST explicitly reply to me when done. Do not finish silently.

1. Save the complete filled-in JSON to `/tmp/bench_ltsv_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input.name="matt-cutts-30days", test_input.url="https://www.youtube.com/watch?v=UNP03fDSj1U", test_input.duration_s=207
- task: name="long-to-short-video", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.asset_acquisition: null (download is internal to S1 skill stage)
- phases.execution.steps: 4 entries:
  - {name:"t1_fresh_3clips_tiktok", duration_s, notes:"s1_apify_s=X s1_download_s=X s1_face_s=X s2_whisper_s=X s3_llm_s=X s4s5s6_per_clip_s=X s7_upload_s=X clips=3"}
  - {name:"t2_cache_hit", duration_s, notes:"cache_status=hit/miss s4s5s6_per_clip_s=X s7_upload_s=X clips=3"}
  - {name:"t3_fresh_3clips_hormozi", duration_s, notes:"s1_apify_s=X s1_download_s=X s2_whisper_s=X s3_llm_s=X clips=3"}
  - {name:"t4_fresh_5clips_tiktok", duration_s, notes:"s1_apify_s=X s2_whisper_s=X s3_llm_s=X clips=5"}
- phases.delivery: upload_s = sum of all S7 CDN uploads across T1+T2+T3+T4, output_url = T1 clip 1 CDN URL
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct
- tokens and cost: from session JSONL parsing

Note: if AV1 hardware decode is unavailable (pod env), face timeline runs ~60s extra (software decode). Record in meta.notes.

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session (e.g. `claude --model sonnet` for Sonnet). Send this prompt:

````
Run a full e2e performance benchmark of the long-to-short-video skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/long-to-short-video/
- Script: ~/code/nova3-agent-skills/long-to-short-video/scripts/long_to_short.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- Requires: ffmpeg, OpenCV (cv2), faster-whisper or Whisper, yt-dlp (fallback downloader)
- No install step.

## Pre-flight

```bash
ffmpeg -version 2>&1 | head -1
python3 -c "import cv2; print('cv2 ok')"
yt-dlp --version
source ~/keys/.env
echo "PIKA_API_BASE_URL=${PIKA_API_BASE_URL:0:30}..."
```

## Steps

1. Clean and wall start:
   ```bash
   rm -rf /tmp/lts_t1 /tmp/lts_t3 /tmp/lts_t4 2>/dev/null
   rm -f /tmp/bench_ltsv_t*.txt 2>/dev/null
   WALL_START=$(date +%s%N); echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/long-to-short-video/scripts/long_to_short.py
   TEST_URL="https://www.youtube.com/watch?v=UNP03fDSj1U"
   ```

2. T1 — full pipeline, 3 clips, tiktok, fresh:
   ```bash
   mkdir -p /tmp/lts_t1
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev \
     > /tmp/bench_ltsv_t1_stdout.txt 2>/tmp/bench_ltsv_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_fresh_3clips_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_ltsv_t1_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_ltsv_t1_stdout.txt'))
       clips = d.get('clips', [])
       print(f'success={d.get(\"success\")} clips={len(clips)} source_duration={d.get(\"source_duration\")}s')
       for i, c in enumerate(clips):
           print(f'  clip{i+1}: virality={c.get(\"virality_score\")} cdn={str(c.get(\"cdn_url\",\"\"))[:60]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_ltsv_t1_stdout.txt').read()[:400])
   "
   ```

3. T2 — cache hit, same --out dir as T1:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev \
     > /tmp/bench_ltsv_t2_stdout.txt 2>/tmp/bench_ltsv_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_cache_hit: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr (look for 'cache hit') ===" && cat /tmp/bench_ltsv_t2_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_ltsv_t2_stdout.txt'))
       clips = d.get('clips', [])
       print(f'success={d.get(\"success\")} clips={len(clips)}')
   except Exception as e:
       print(f'parse error: {e}')
   "
   ```

4. T3 — hormozi style, 3 clips, fresh:
   ```bash
   mkdir -p /tmp/lts_t3
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style hormozi --out /tmp/lts_t3 --dev \
     > /tmp/bench_ltsv_t3_stdout.txt 2>/tmp/bench_ltsv_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_hormozi_3clips: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_ltsv_t3_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_ltsv_t3_stdout.txt'))
       print(f'clips={len(d.get(\"clips\",[]))}')
   except Exception as e:
       print(f'parse error: {e}')
   "
   ```

5. T4 — 5 clips, tiktok, fresh:
   ```bash
   mkdir -p /tmp/lts_t4
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 5 --style tiktok --out /tmp/lts_t4 --dev \
     > /tmp/bench_ltsv_t4_stdout.txt 2>/tmp/bench_ltsv_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_5clips_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_ltsv_t4_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_ltsv_t4_stdout.txt'))
       clips = d.get('clips', [])
       print(f'clips={len(clips)}')
       for i, c in enumerate(clips):
           print(f'  clip{i+1}: virality={c.get(\"virality_score\")}')
   except Exception as e:
       print(f'parse error: {e}')
   "
   ```

6. Wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## Sub-stage timing (from --dev stderr)

Parse `/tmp/bench_ltsv_tN_stderr.txt` for these markers:
- `S1 got download URL in Xs` → Apify API call duration
- `S1 ✅ downloaded XMB in Xs` → actual file download to disk
- `S1 ✅ Video cache hit` → T2 cache confirmed
- `S2 ✅ Transcribed ... in Xs` → Whisper transcription duration
- `S3 ✅ Selected N clips ... in Xs` → LLM clip selection
- `S5 Face trajectory: N detections` → OpenCV face detection (time = elapsed between S4 and S5)
- `S7 ✅ Clip N ready` → CDN upload time per clip

Fill each step's notes field with: `s1_apify_s=X s1_download_s=X s1_face_s=X s2_whisper_s=X s3_llm_s=X s7_upload_per_clip_s=X`

## Token tracking

```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_long-to-short-video_run1/result.json

Key values:
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- phases.install: null
- phases.asset_acquisition: null (download is inside S1)
- phases.execution.steps: 4 entries (t1_fresh_3clips_tiktok, t2_cache_hit, t3_fresh_3clips_hormozi, t4_fresh_5clips_tiktok)
- phases.delivery: upload_s = total S7 CDN time (all clips), output_url = T1 clip 1 CDN URL
- meta.notes: note if AV1 hw decode was unavailable (adds ~60s to face timeline per fresh run)

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Managed Claude Agent Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the long-to-short-video skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/keys/.env` (ANTHROPIC_API_KEY)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `<TBD — to be filled when MCA environment for LTSV is provisioned>`
- Environment ID: `<TBD>`
- The environment needs: PIKA_API_BASE_URL, PIKA_AGENT_API_KEY injected; ffmpeg, OpenCV (cv2), yt-dlp, Whisper installed; nova3-agent-skills at /workspace/skills/
- **CRITICAL:** T1/T3/T4 full pipeline runs take 2-8 minutes each. The bash tool has a 295s timeout. You MUST use nohup + background + poll for ALL pipeline runs.

## Steps

1. Clean: `rm -f /tmp/bench_mca_ltsv_* 2>/dev/null`

2. Source API key and create session:
   ```bash
   export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/keys/.env | cut -d= -f2)
   AGENT_ID="<TBD>"
   ENV_ID="<TBD>"
   WALL_START=$(date +%s%N); echo "WALL_START=$WALL_START"
   SESSION=$(curl -sS https://api.anthropic.com/v1/sessions \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d "{
       \"agent\": \"$AGENT_ID\",
       \"environment_id\": \"$ENV_ID\",
       \"title\": \"Benchmark: long-to-short-video $(date +%Y-%m-%d_%H%M)\"
     }")
   SESSION_ID=$(echo "$SESSION" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])")
   echo "Session: $SESSION_ID"
   ```

3. Send the task message (uses nohup for all 4 test cases due to 295s bash timeout):
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{
       "events": [{
         "type": "user.message",
         "content": [{"type": "text", "text": "Run 4 test cases for the long-to-short-video skill. ALL pipeline runs take 2-8 min — you MUST use nohup + background + poll pattern for each. Prepend your ENVIRONMENT SETUP exports to every python command.\n\nSKILL=/workspace/skills/long-to-short-video/scripts/long_to_short.py\nTEST_URL=\"https://www.youtube.com/watch?v=UNP03fDSj1U\"\n\n## Preparation\n```bash\nrm -rf /tmp/lts_t1 /tmp/lts_t3 /tmp/lts_t4; mkdir -p /tmp/lts_t1 /tmp/lts_t3 /tmp/lts_t4\n```\n\n## T1 — fresh 3-clip tiktok (nohup required)\n```bash\nT_START_T1=$(date +%s%N)\nnohup bash -c 'python3 '$SKILL' --input \"'$TEST_URL'\" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev > /tmp/t1_out.json 2>/tmp/t1_err.txt; echo DONE > /tmp/t1_done.txt' > /tmp/t1_nohup.log 2>&1 &\necho \"T1 PID: $!\"\n```\nPoll:\n```bash\nwhile ! [ -f /tmp/t1_done.txt ]; do sleep 15; done\nT_END_T1=$(date +%s%N)\necho \"T1_ms: $(( (T_END_T1 - T_START_T1) / 1000000 ))\"\ncat /tmp/t1_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t1_out.json')); clips=d.get('clips',[]); print(f'clips={len(clips)}'); [print(f'  clip{i+1}: virality={c.get(\\\"virality_score\\\")} cdn={str(c.get(\\\"cdn_url\\\",\\\"\\\"))[:60]}') for i,c in enumerate(clips)]\"\n```\n\n## T2 — cache hit (same --out /tmp/lts_t1, nohup required)\n```bash\nT_START_T2=$(date +%s%N)\nnohup bash -c 'python3 '$SKILL' --input \"'$TEST_URL'\" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev > /tmp/t2_out.json 2>/tmp/t2_err.txt; echo DONE > /tmp/t2_done.txt' > /tmp/t2_nohup.log 2>&1 &\necho \"T2 PID: $!\"\n```\nPoll:\n```bash\nwhile ! [ -f /tmp/t2_done.txt ]; do sleep 10; done\nT_END_T2=$(date +%s%N)\necho \"T2_ms: $(( (T_END_T2 - T_START_T2) / 1000000 ))\"\ncat /tmp/t2_err.txt\n```\n\n## T3 — hormozi 3-clip fresh\n```bash\nT_START_T3=$(date +%s%N)\nnohup bash -c 'python3 '$SKILL' --input \"'$TEST_URL'\" --num-clips 3 --style hormozi --out /tmp/lts_t3 --dev > /tmp/t3_out.json 2>/tmp/t3_err.txt; echo DONE > /tmp/t3_done.txt' > /tmp/t3_nohup.log 2>&1 &\necho \"T3 PID: $!\"\n```\nPoll:\n```bash\nwhile ! [ -f /tmp/t3_done.txt ]; do sleep 15; done\nT_END_T3=$(date +%s%N)\necho \"T3_ms: $(( (T_END_T3 - T_START_T3) / 1000000 ))\"\ncat /tmp/t3_err.txt\n```\n\n## T4 — 5-clip tiktok fresh\n```bash\nT_START_T4=$(date +%s%N)\nnohup bash -c 'python3 '$SKILL' --input \"'$TEST_URL'\" --num-clips 5 --style tiktok --out /tmp/lts_t4 --dev > /tmp/t4_out.json 2>/tmp/t4_err.txt; echo DONE > /tmp/t4_done.txt' > /tmp/t4_nohup.log 2>&1 &\necho \"T4 PID: $!\"\n```\nPoll:\n```bash\nwhile ! [ -f /tmp/t4_done.txt ]; do sleep 15; done\nT_END_T4=$(date +%s%N)\necho \"T4_ms: $(( (T_END_T4 - T_START_T4) / 1000000 ))\"\ncat /tmp/t4_err.txt\n```\n\nReport T1/T2/T3/T4 durations and clip counts. Also note any 'cache hit' messages in T2 stderr."}]
       }]
     }'
   ```

4. Poll session status every 10s until `idle` or `terminated` (timeout 40 min — all 4 runs serial):
   ```bash
   POLL_START=$(date +%s)
   while true; do
     STATUS=$(curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -H "anthropic-beta: managed-agents-2026-04-01")
     STATE=$(echo "$STATUS" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['status'])")
     echo "$(date +%T) status=$STATE"
     if [ "$STATE" = "idle" ] || [ "$STATE" = "terminated" ]; then break; fi
     if [ $(( $(date +%s) - POLL_START )) -gt 2400 ]; then echo "TIMEOUT after 40min"; break; fi
     sleep 10
   done
   ```

5. Record wall end and fetch metadata:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_ltsv_session.json | python3 -m json.tool
   ```

6. Fetch events and extract timing:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_ltsv_events.json \
     | python3 -c "
   import json,sys
   from datetime import datetime
   def parse_ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
   events = json.loads(sys.stdin.read())['data']
   t0 = parse_ts([e for e in events if e['type']=='session.status_running'][0]['processed_at'])
   t_end = parse_ts([e for e in events if e['type']=='session.status_idle'][0]['processed_at'])
   pending = {}; tool_total = 0
   for e in events:
       if e['type'] == 'agent.tool_use':
           pending[e['id']] = {'name': e.get('name',''), 'start': e['processed_at'],
                               'input': str(e.get('input',{}).get('command',''))[:100]}
       elif e['type'] == 'agent.tool_result' and e.get('tool_use_id') in pending:
           tc = pending.pop(e['tool_use_id'])
           dur = (parse_ts(e['processed_at']) - parse_ts(tc['start'])).total_seconds()
           tool_total += dur
           err = ' [ERROR]' if e.get('is_error') else ''
           print(f'{tc[\"name\"]:6s} {dur:8.1f}s{err}  {tc[\"input\"]}')
   wall = (t_end - t0).total_seconds()
   print(f'wall_total_s: {wall:.3f}')
   print(f'tool_calls_s: {tool_total:.3f}')
   print(f'llm_overhead_s: {wall - tool_total:.3f}')
   print(f'llm_pct: {(wall - tool_total) / wall * 100:.1f}%')
   "
   ```

## Token & cost tracking

```bash
python3 -c "
import json
with open('/tmp/bench_mca_ltsv_session.json') as f:
    s = json.loads(f.read())
u = s['usage']
inp = u['input_tokens']; out = u['output_tokens']
cr = u.get('cache_read_input_tokens', 0)
cw = (u.get('cache_creation') or {}).get('ephemeral_5m_input_tokens', 0)
total = inp + out + cr + cw
cost = (inp*3 + out*15 + cr*0.30 + cw*3.75) / 1_000_000
print(f'input_tokens: {inp}'); print(f'output_tokens: {out}')
print(f'cache_read_tokens: {cr}'); print(f'cache_write_tokens: {cw}')
print(f'total_tokens: {total}'); print(f'estimated_cost_usd: {cost:.4f}')
"
```

## Output

Save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_long-to-short-video_runN/result.json

Key values:
- platform.name: "managed-claude-agent"
- phases.install, phases.asset_acquisition: null
- phases.execution.steps: 4 entries
- Note whether T2 confirmed "cache hit" in stderr (S1 and face timeline skipped)
- Note if AV1 hw decode was available in the MCA container

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`
````

---

## Codex Prompt

Start a Codex session. Send this prompt:

````
Run a full e2e performance benchmark of the long-to-short-video skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/long-to-short-video/
- Script: ~/code/nova3-agent-skills/long-to-short-video/scripts/long_to_short.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- Requires: ffmpeg, OpenCV (cv2), yt-dlp, Whisper/faster-whisper
- No install step.

## Steps

1. Pre-flight + wall start:
   ```bash
   ffmpeg -version 2>&1 | head -1 && python3 -c "import cv2; print('cv2 ok')" && yt-dlp --version
   source ~/keys/.env
   rm -rf /tmp/lts_t1 /tmp/lts_t3 /tmp/lts_t4; rm -f /tmp/bench_ltsv_t*.txt 2>/dev/null
   WALL_START=$(date +%s%N); echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/long-to-short-video/scripts/long_to_short.py
   TEST_URL="https://www.youtube.com/watch?v=UNP03fDSj1U"
   ```

2. T1 — fresh 3-clip tiktok:
   ```bash
   mkdir -p /tmp/lts_t1
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev \
     > /tmp/bench_ltsv_t1_stdout.txt 2>/tmp/bench_ltsv_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_fresh_3clips_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_ltsv_t1_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_ltsv_t1_stdout.txt'))
   clips=d.get('clips',[]); print(f'clips={len(clips)} duration={d.get(\"source_duration\")}s')
   [print(f'  clip{i+1}: virality={c.get(\"virality_score\")} cdn={str(c.get(\"cdn_url\",\"\"))[:60]}') for i,c in enumerate(clips)]
   "
   ```

3. T2 — cache hit (same --out /tmp/lts_t1):
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style tiktok --out /tmp/lts_t1 --dev \
     > /tmp/bench_ltsv_t2_stdout.txt 2>/tmp/bench_ltsv_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_cache_hit: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr ===" && cat /tmp/bench_ltsv_t2_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_ltsv_t2_stdout.txt'))
   print(f'clips={len(d.get(\"clips\",[]))}')
   "
   ```

4. T3 — hormozi style fresh:
   ```bash
   mkdir -p /tmp/lts_t3
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 3 --style hormozi --out /tmp/lts_t3 --dev \
     > /tmp/bench_ltsv_t3_stdout.txt 2>/tmp/bench_ltsv_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_hormozi_3clips: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_ltsv_t3_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_ltsv_t3_stdout.txt'))
   print(f'clips={len(d.get(\"clips\",[]))}')
   "
   ```

5. T4 — 5-clip tiktok fresh:
   ```bash
   mkdir -p /tmp/lts_t4
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --input "$TEST_URL" --num-clips 5 --style tiktok --out /tmp/lts_t4 --dev \
     > /tmp/bench_ltsv_t4_stdout.txt 2>/tmp/bench_ltsv_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_5clips_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_ltsv_t4_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_ltsv_t4_stdout.txt'))
   clips=d.get('clips',[]); print(f'clips={len(clips)}')
   [print(f'  clip{i+1}: virality={c.get(\"virality_score\")}') for i,c in enumerate(clips)]
   "
   ```

6. Wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## Token tracking

```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_long-to-short-video_run1/result.json

Key values:
- platform.name: "codex"
- phases.install, phases.asset_acquisition: null
- phases.execution.steps: 4 entries
- phases.delivery: upload_s = sum of S7 CDN upload times, output_url = T1 clip 1 CDN URL
- meta.notes: note AV1 hw decode availability (affects face timeline time)

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **Test video:** https://www.youtube.com/watch?v=UNP03fDSj1U — Matt Cutts "Try Something New for 30 Days" (3m27s). Short enough to be processable but long enough to select 5 clips.
- **T2 cache hit behavior (v1.0.x+):** T2 reuses `/tmp/lts_t1`. `source.mp4` + `source.mp4.meta.json` persist from T1 (download cache). `source.mp4.face_timeline.json` also persists (face timeline cache). `audio.mp3` was deleted at T1 end (re-derived). Expected T2 time: ~20-40s (only S3 LLM re-runs + S4/S5/S6/S7 per-clip). Verify with "cache hit" in T2 stderr.
- **AV1 hardware decode:** EKS pods lack AV1 hw decode — software decode adds ~60s to face timeline (`build_face_timeline`) per fresh run. Devbox/MCA containers may support hw decode. Note in meta.notes.
- **Pipeline stages in --dev mode:**
  - S1: Apify download (dc_solutions primary, scraper_one fallback, yt-dlp last resort) + face timeline (OpenCV)
  - S2: Whisper transcription (via Pika proxy)
  - S3: LLM clip selection (Anthropic)
  - S4: raw clip trim (ffmpeg)
  - S5: face trajectory keyframe detection
  - S6: caption burn-in (ffmpeg)
  - S7: CDN upload (per clip)
- **Expected timings (EKS pod, AV1 software decode):** T1 ~200-370s, T2 ~20-40s (cache), T3 ~200-370s, T4 ~250-450s. Devbox with hw decode: T1 ~120-180s.
- **Managed Claude Agent:** Agent ID and Env ID TBD. Environment must include ffmpeg, cv2, Whisper, yt-dlp. Timeout budget: 40 min for all 4 runs serial.

## Processing PikaBot Results

When PikaBot sends back the result JSON (CDN URL or pasted):

1. Download:
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_ltsv_result.json
   ```

2. Save to run dir:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_long-to-short-video_runN
   mkdir -p "$RUN_DIR" && cp /tmp/pikabot_ltsv_result.json "$RUN_DIR/result.json"
   ```

3. Validate:
   ```bash
   python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py "$RUN_DIR"
   ```
