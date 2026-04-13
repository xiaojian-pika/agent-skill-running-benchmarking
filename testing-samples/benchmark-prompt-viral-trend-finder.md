# Benchmark Prompt: viral-trend-finder

> **Skill:** viral-trend-finder
> **Test cases:** T1 find fitness (TikTok+Instagram), T2 find cooking (X), T3 analyze full pipeline, T4 trending (general)
> **Expected output:** JSON with trend results / storyboard + hook copy per test case
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the viral-trend-finder skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Run 4 test cases in order:
- T1: `find "fitness" --platforms tiktok,instagram --count 5`
- T2: `find "cooking" --platforms x --count 5`
- T3: `analyze <first URL from T1 results>` (full pipeline: download + frames + Gemini + LLM synthesis)
- T4: `trending` (no arguments — general trending content)

## Steps

1. Clean: `rm -f /tmp/bench_vtf_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"`
3. Install skill "viral-trend-finder" from Pika Staging Skill Hub (CMS). Time each sub-step (cms_fetch, skill_install, subagent_start).
4. Run T1, T2, T3, T4 in sequence. Time each one individually.
   - After T1: extract the first valid video URL from the results and save it for T3.
   - For T3: if T1 returned no results, use fallback URL `https://www.tiktok.com/@khaby.lame/video/7000000000000000000`.
   - Capture full stderr for each run (VTF logs progress to stderr: metadata fetch → download → frame extract → Gemini → synthesis).
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`

## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- VTF does NOT emit ⏱️ timing lines — infer T3 sub-stages from stderr progress messages:
  - `Fetching metadata` → metadata start; `Downloading video` → download start
  - `Downloaded:` → download end / frame extract start; `Extracted N frames` → frame extract end
  - `Frame N/M done` → Gemini progress; `Synthesizing analysis` → LLM start; `Analysis saved` → LLM end
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

1. Save the complete filled-in JSON to `/tmp/bench_vtf_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input.name="social-trend-queries", test_input.description="fitness(TikTok+IG), cooking(X), analyze(T1 URL), trending"
- task: name="viral-trend-finder", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.asset_acquisition: null (video download is internal to T3 skill execution)
- phases.execution.steps: 4 entries — t1_find_fitness, t2_find_cooking_x, t3_analyze, t4_trending
  - For t3_analyze: include sub-stages in notes field (metadata_s, download_s, frame_extract_s, gemini_vision_s, llm_synthesis_s inferred from stderr)
- phases.delivery: upload_s for result JSON, output_url = CDN URL of result JSON
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct
- tokens and cost: from session JSONL parsing

Also include a brief text summary of observations (e.g. T1/T2 result counts, T3 pipeline stages, any X API empty-results issue).

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session (e.g. `claude --model sonnet` for Sonnet). Send this prompt:

````
Run a full e2e performance benchmark of the viral-trend-finder skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/viral-trend-finder/
- Script: ~/code/nova3-agent-skills/viral-trend-finder/scripts/viral_trend_finder.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY, GOOGLE_API_KEY)
- No install step. T3 analyze requires ffmpeg and yt-dlp (check both are installed before starting).

## Steps

1. Pre-flight check:
   ```bash
   ffmpeg -version 2>&1 | head -1
   yt-dlp --version
   source ~/keys/.env
   echo "API keys: PIKA_API_BASE_URL=${PIKA_API_BASE_URL:0:30}..."
   ```

2. Clean and record wall start:
   ```bash
   rm -f /tmp/bench_vtf_* 2>/dev/null
   WALL_START=$(date +%s%N)
   echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/viral-trend-finder/scripts/viral_trend_finder.py
   ```

3. T1 — find fitness on TikTok + Instagram:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" find "fitness" --platforms tiktok,instagram --count 5 \
     > /tmp/bench_vtf_t1_stdout.txt 2>/tmp/bench_vtf_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_find_fitness: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_vtf_t1_stderr.txt
   python3 -c "
   import json
   try:
       data = json.load(open('/tmp/bench_vtf_t1_stdout.txt'))
       results = data.get('results', data) if isinstance(data, dict) else data
       if not isinstance(results, list): results = []
       print(f'results_count={len(results)}')
       for i, r in enumerate(results[:3]):
           url = r.get('url') or r.get('video_url', '')
           print(f'  [{i+1}] platform={r.get(\"platform\")} views={r.get(\"views\",\"?\")} url={url[:80]}')
       urls = [r.get('url') or r.get('video_url','') for r in results if r.get('url') or r.get('video_url')]
       first_url = next((u for u in urls if u), '')
       open('/tmp/bench_vtf_t3_url.txt', 'w').write(first_url)
       print(f'T3_url={first_url[:80]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_vtf_t1_stdout.txt').read()[:400])
   "
   ```

4. T2 — find cooking on X/Twitter:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" find "cooking" --platforms x --count 5 \
     > /tmp/bench_vtf_t2_stdout.txt 2>/tmp/bench_vtf_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_find_cooking_x: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr ===" && cat /tmp/bench_vtf_t2_stderr.txt
   python3 -c "
   import json
   try:
       data = json.load(open('/tmp/bench_vtf_t2_stdout.txt'))
       results = data.get('results', data) if isinstance(data, dict) else data
       if not isinstance(results, list): results = []
       print(f'results_count={len(results)}')
       for i, r in enumerate(results[:3]):
           print(f'  [{i+1}] platform={r.get(\"platform\")} views={r.get(\"views\",\"?\")} url={str(r.get(\"url\",\"\"))[:80]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_vtf_t2_stdout.txt').read()[:400])
   "
   ```

5. T3 — analyze full pipeline:
   ```bash
   T3_URL=$(cat /tmp/bench_vtf_t3_url.txt 2>/dev/null || echo "")
   if [ -z "$T3_URL" ]; then
     T3_URL="https://www.tiktok.com/@khaby.lame/video/7000000000000000000"
     echo "T1 had no results — using fallback URL"
   fi
   echo "T3_URL=$T3_URL"
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" analyze "$T3_URL" \
     > /tmp/bench_vtf_t3_stdout.txt 2>/tmp/bench_vtf_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_analyze: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_vtf_t3_stderr.txt
   python3 -c "
   import json
   try:
       data = json.load(open('/tmp/bench_vtf_t3_stdout.txt'))
       shots = data.get('shots', data.get('storyboard', []))
       print(f'success={data.get(\"success\", True)}')
       print(f'title={str(data.get(\"title\",\"\"))[:60]}')
       print(f'duration={data.get(\"duration\")}s  shots={len(shots)}  frames={data.get(\"frames_analyzed\",\"?\")}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_vtf_t3_stdout.txt').read()[:500])
   "
   ```

6. T4 — trending (general, no niche):
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" trending \
     > /tmp/bench_vtf_t4_stdout.txt 2>/tmp/bench_vtf_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_trending: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_vtf_t4_stderr.txt
   python3 -c "
   import json
   try:
       data = json.load(open('/tmp/bench_vtf_t4_stdout.txt'))
       results = data.get('results', data) if isinstance(data, dict) else data
       if not isinstance(results, list): results = []
       print(f'results_count={len(results)}')
       for i, r in enumerate(results[:3]):
           print(f'  [{i+1}] platform={r.get(\"platform\")} views={r.get(\"views\",\"?\")}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_vtf_t4_stdout.txt').read()[:300])
   "
   ```

7. Record wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## T3 sub-stage timing (inferred from stderr)

VTF does not emit ⏱️ lines. Parse progress messages from `/tmp/bench_vtf_t3_stderr.txt`:
- Line containing `Fetching metadata` → S1 metadata start
- Line containing `Downloading video` → S2 download start
- Line containing `Downloaded:` → S2 download end / S3 frame extract start
- Line containing `Extracted N frames` → S3 frame extract end / S4 Gemini start
- Line containing `Frame N/M done` (final) → S4 Gemini end
- Line containing `Synthesizing analysis` → S5 LLM start
- Line containing `Analysis saved` → S5 LLM end

Record these in the `t3_analyze` step's notes field as: `metadata_s=X download_s=X frame_extract_s=X gemini_vision_s=X llm_synthesis_s=X`

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_viral-trend-finder_run1/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- platform.llm_model: your model name
- phases.install: all null (no install)
- phases.asset_acquisition: null (video download internal to T3 skill)
- phases.execution.steps: [{name:"t1_find_fitness", duration_s, notes:"tiktok_s=X ig_s=X results=N"}, {name:"t2_find_cooking_x", duration_s, notes:"results=N"}, {name:"t3_analyze", duration_s, notes:"metadata_s=X download_s=X frame_extract_s=X gemini_vision_s=X llm_synthesis_s=X shots=N frames=N"}, {name:"t4_trending", duration_s, notes:"results=N"}]
- phases.delivery.upload_s: 0 (no CDN upload)
- tokens: fill from session stats
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Managed Claude Agent Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the viral-trend-finder skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/keys/.env` (ANTHROPIC_API_KEY)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `<TBD — to be filled when MCA environment for VTF is provisioned>`
- Environment ID: `<TBD>`
- The environment needs: PIKA_API_BASE_URL, PIKA_AGENT_API_KEY, GOOGLE_API_KEY injected; ffmpeg + yt-dlp installed; nova3-agent-skills at /workspace/skills/
- **T3 note:** `analyze` calls yt-dlp to download a video + runs ffmpeg frame extraction. Both must be available in the container. The bash tool has a 295s timeout — use nohup + background + poll pattern for T3.

## Steps

1. Clean: `rm -f /tmp/bench_mca_vtf_* 2>/dev/null`

2. Source API key and create session:
   ```bash
   export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/keys/.env | cut -d= -f2)
   AGENT_ID="<TBD>"
   ENV_ID="<TBD>"
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
       \"title\": \"Benchmark: viral-trend-finder $(date +%Y-%m-%d_%H%M)\"
     }")
   SESSION_ID=$(echo "$SESSION" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])")
   echo "Session: $SESSION_ID"
   ```

3. Send the task message:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{
       "events": [{
         "type": "user.message",
         "content": [{"type": "text", "text": "Run 4 test cases for the viral-trend-finder skill. Prepend your ENVIRONMENT SETUP exports to every python command.\n\nSKILL_SCRIPT=/workspace/skills/viral-trend-finder/scripts/viral_trend_finder.py\n\nT1 — find fitness (TikTok+Instagram):\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT find \"fitness\" --platforms tiktok,instagram --count 5 > /tmp/t1_out.json 2>/tmp/t1_err.txt\nT_END=$(date +%s%N)\necho \"T1_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t1_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t1_out.json')); r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []; print(f'results={len(r)}'); urls=[x.get('url') or x.get('video_url','') for x in r if x.get('url') or x.get('video_url')]; open('/tmp/t3_url.txt','w').write(urls[0] if urls else '')\"\n```\n\nT2 — find cooking (X):\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT find \"cooking\" --platforms x --count 5 > /tmp/t2_out.json 2>/tmp/t2_err.txt\nT_END=$(date +%s%N)\necho \"T2_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t2_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t2_out.json')); r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []; print(f'results={len(r)}')\"\n```\n\nT3 — analyze (full pipeline). Use URL from /tmp/t3_url.txt or fallback if empty. IMPORTANT: use nohup + background + poll (bash timeout is 295s):\n```bash\nT3_URL=$(cat /tmp/t3_url.txt 2>/dev/null || echo '')\n[ -z \"$T3_URL\" ] && T3_URL='https://www.tiktok.com/@khaby.lame/video/7000000000000000000'\necho \"T3_URL=$T3_URL\"\nnohup bash -c '\nT_START=$(date +%s%N)\npython3 '$SKILL_SCRIPT' analyze \"'$T3_URL'\" > /tmp/t3_out.json 2>/tmp/t3_err.txt\nT_END=$(date +%s%N)\necho \"T3_ms: $(( (T_END - T_START) / 1000000 ))\" > /tmp/t3_timing.txt\necho DONE >> /tmp/t3_timing.txt\n' > /tmp/t3_nohup.log 2>&1 &\necho \"PID: $!\"\n```\nThen poll every 10s:\n```bash\nwhile ! grep -q DONE /tmp/t3_timing.txt 2>/dev/null; do sleep 10; done\ncat /tmp/t3_timing.txt\ncat /tmp/t3_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t3_out.json')); shots=d.get('shots',d.get('storyboard',[])); print(f'shots={len(shots)} frames={d.get(\\\"frames_analyzed\\\",\\\"?\\\")}')\"\n```\n\nT4 — trending (general):\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT trending > /tmp/t4_out.json 2>/tmp/t4_err.txt\nT_END=$(date +%s%N)\necho \"T4_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t4_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t4_out.json')); r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []; print(f'results={len(r)}')\"\n```\n\nReport all T1/T2/T3/T4 timings and result counts."}]
       }]
     }'
   ```

4. Poll session status every 5s until `idle` or `terminated` (timeout 15 min for T3):
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
     if [ $(( $(date +%s) - POLL_START )) -gt 900 ]; then echo "TIMEOUT after 15min"; break; fi
     sleep 5
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
     | tee /tmp/bench_mca_vtf_session.json | python3 -m json.tool
   ```

6. Fetch events and extract timing:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_vtf_events.json \
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
                               'input': str(e.get('input',{}).get('command',''))[:120]}
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
with open('/tmp/bench_mca_vtf_session.json') as f:
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
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_viral-trend-finder_runN/result.json

Key values:
- platform.name: "managed-claude-agent"
- phases.install: null
- phases.asset_acquisition: null
- phases.execution.steps: 4 entries (t1_find_fitness, t2_find_cooking_x, t3_analyze, t4_trending)
- For t3_analyze note: `metadata_s=X download_s=X frame_extract_s=X gemini_vision_s=X llm_synthesis_s=X` (inferred from stderr)

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`
````

---

## Codex Prompt

Start a Codex session. Send this prompt:

````
Run a full e2e performance benchmark of the viral-trend-finder skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/viral-trend-finder/
- Script: ~/code/nova3-agent-skills/viral-trend-finder/scripts/viral_trend_finder.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY, GOOGLE_API_KEY)
- No install step. T3 analyze requires ffmpeg and yt-dlp.

## Steps

1. Pre-flight + wall start:
   ```bash
   ffmpeg -version 2>&1 | head -1 && yt-dlp --version
   source ~/keys/.env
   rm -f /tmp/bench_vtf_* 2>/dev/null
   WALL_START=$(date +%s%N); echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/viral-trend-finder/scripts/viral_trend_finder.py
   ```

2. T1 — find fitness (TikTok+Instagram):
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" find "fitness" --platforms tiktok,instagram --count 5 \
     > /tmp/bench_vtf_t1_stdout.txt 2>/tmp/bench_vtf_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_find_fitness: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_vtf_t1_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_vtf_t1_stdout.txt'))
   r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []
   print(f'results={len(r)}')
   urls=[x.get('url') or x.get('video_url','') for x in r if x.get('url') or x.get('video_url')]
   open('/tmp/bench_vtf_t3_url.txt','w').write(urls[0] if urls else '')
   print(f'T3_url={urls[0][:80] if urls else \"(none)\"}')
   "
   ```

3. T2 — find cooking (X):
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" find "cooking" --platforms x --count 5 \
     > /tmp/bench_vtf_t2_stdout.txt 2>/tmp/bench_vtf_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_find_cooking_x: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr ===" && cat /tmp/bench_vtf_t2_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_vtf_t2_stdout.txt'))
   r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []
   print(f'results={len(r)}')
   "
   ```

4. T3 — analyze full pipeline:
   ```bash
   T3_URL=$(cat /tmp/bench_vtf_t3_url.txt 2>/dev/null || echo "")
   [ -z "$T3_URL" ] && T3_URL="https://www.tiktok.com/@khaby.lame/video/7000000000000000000" && echo "Using fallback URL"
   echo "T3_URL=$T3_URL"
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" analyze "$T3_URL" \
     > /tmp/bench_vtf_t3_stdout.txt 2>/tmp/bench_vtf_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_analyze: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_vtf_t3_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_vtf_t3_stdout.txt'))
   shots=d.get('shots',d.get('storyboard',[]))
   print(f'shots={len(shots)} frames={d.get(\"frames_analyzed\",\"?\")} duration={d.get(\"duration\",\"?\")}s')
   "
   ```

5. T4 — trending:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" trending \
     > /tmp/bench_vtf_t4_stdout.txt 2>/tmp/bench_vtf_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_trending: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_vtf_t4_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_vtf_t4_stdout.txt'))
   r=d.get('results',d) if isinstance(d,dict) else d; r=r if isinstance(r,list) else []
   print(f'results={len(r)}')
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
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_viral-trend-finder_run1/result.json

Key values:
- platform.name: "codex"
- phases.install, phases.asset_acquisition: null
- phases.execution.steps: 4 entries (t1_find_fitness, t2_find_cooking_x, t3_analyze, t4_trending)
- phases.delivery.upload_s: 0

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **No CDN upload:** VTF outputs JSON to stdout only. `phases.delivery` upload_s = 0 for all platforms.
- **T3 analyze sub-stages (inferred from stderr):** VTF does not emit ⏱️ timing lines. Infer from push_dev progress messages: `Fetching metadata` / `Downloading video` / `Downloaded:` / `Extracted N frames` / `Frame N/M done` / `Synthesizing analysis` / `Analysis saved`. Record estimates in the t3_analyze step's notes field.
- **T3 mode:** If yt-dlp fails (TikTok bot detection, geo-block), skill may fall back to metadata-only analysis. Record as `T3_mode: full_pipeline` or `metadata_only` in meta.notes.
- **X/Twitter reliability:** RapidAPI may return 0 results intermittently. Note in meta.notes if T2 returns empty.
- **Managed Claude Agent:** Agent ID and Environment ID are TBD — fill in once a VTF-compatible MCA environment (with ffmpeg + yt-dlp + GOOGLE_API_KEY) is provisioned.
- **API key location (devbox):** `~/keys/.env` contains PIKA_API_BASE_URL, PIKA_AGENT_API_KEY, and GOOGLE_API_KEY.
- **T3 pipeline time:** Expect ~60-180s (yt-dlp download + ffmpeg frame extract + Gemini per-frame calls + LLM synthesis). Use nohup + background + poll on MCA to avoid bash 295s timeout.

## Processing PikaBot Results

When PikaBot sends back the result JSON (CDN URL or pasted):

1. Download:
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_vtf_result.json
   ```

2. Save to run dir:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_viral-trend-finder_runN
   mkdir -p "$RUN_DIR" && cp /tmp/pikabot_vtf_result.json "$RUN_DIR/result.json"
   ```

3. Validate:
   ```bash
   python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py "$RUN_DIR"
   ```
