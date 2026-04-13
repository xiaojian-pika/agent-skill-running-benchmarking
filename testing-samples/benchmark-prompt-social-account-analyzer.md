# Benchmark Prompt: social-account-analyzer

> **Skill:** social-account-analyzer
> **Test cases:** @natgeo (Instagram), @NASA (X/Twitter), @khaby.lame (TikTok)
> **Expected output:** JSON with profile metrics, engagement analysis, and growth recommendations per account
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the social-account-analyzer skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Analyze 3 social media accounts:
- T1: @natgeo on Instagram
- T2: @NASA on X/Twitter
- T3: @khaby.lame on TikTok

## Steps

1. Clean: `rm -f /tmp/bench_saa_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"`
3. Install skill "social-account-analyzer" from Pika Staging Skill Hub (CMS). Time each sub-step (cms_fetch, skill_install, subagent_start).
4. Run each test case individually and time it:
   - T1 Instagram: `python3 $PIKABOT_SKILLS_DIR/social-account-analyzer/scripts/analyze_account.py analyze "@natgeo" --platform instagram`
   - T2 X/Twitter: `python3 $PIKABOT_SKILLS_DIR/social-account-analyzer/scripts/analyze_account.py analyze "@NASA" --platform x`
   - T3 TikTok: `python3 $PIKABOT_SKILLS_DIR/social-account-analyzer/scripts/analyze_account.py analyze "@khaby.lame" --platform tiktok`
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`

## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- Capture full stderr for each run (contains ⏱️ per-stage timing: fetch + llm)
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

1. Save the complete filled-in JSON to `/tmp/bench_saa_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input.name="social-handles", test_input.description="@natgeo(ig) @NASA(x) @khaby.lame(tiktok)"
- task: name="social-account-analyzer", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.asset_acquisition: all null (no video to download)
- phases.execution.steps: one entry per test case (t1_instagram, t2_x, t3_tiktok), each with fetch_s and llm_s sub-fields in notes
- phases.delivery: upload_s for result JSON, output_url = CDN URL of result JSON
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct
- tokens and cost: from session JSONL parsing

Also include a brief text summary of observations after the JSON (e.g. which platform was slowest, LLM truncation issues, engagement rate accuracy).

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session (e.g. `claude --model sonnet` for Sonnet). Send this prompt:

````
Run a full e2e performance benchmark of the social-account-analyzer skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/social-account-analyzer/
- Script: ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- No install step, no video download

## Steps

1. Clean:
   ```bash
   rm -f /tmp/bench_saa_* 2>/dev/null
   ```

2. Source API keys and record wall start:
   ```bash
   source ~/keys/.env
   WALL_START=$(date +%s%N)
   echo "WALL_START=$WALL_START"
   ```

3. T1 — Instagram @natgeo:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@natgeo" --platform instagram \
     > /tmp/bench_saa_t1_stdout.txt 2>/tmp/bench_saa_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_instagram: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t1_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t1_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t1_stdout.txt').read()[:300])
   "
   ```

4. T2 — X/Twitter @NASA:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@NASA" --platform x \
     > /tmp/bench_saa_t2_stdout.txt 2>/tmp/bench_saa_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_x: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t2_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t2_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t2_stdout.txt').read()[:300])
   "
   ```

5. T3 — TikTok @khaby.lame:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@khaby.lame" --platform tiktok \
     > /tmp/bench_saa_t3_stdout.txt 2>/tmp/bench_saa_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t3_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t3_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t3_stdout.txt').read()[:300])
   "
   ```

6. Record wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Replace `<WALL_START_ISO>` and `<WALL_END_ISO>` with the ISO timestamps (or epoch ms) from your wall start/end steps. The `--after`/`--before` flags isolate tokens to this benchmark task only (important if the session has other work).

This outputs input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, effective_input_tokens, total_tokens, and estimated_cost_usd. Note: with Claude caching, most input tokens appear in cache_read_tokens, not input_tokens. The effective_input_tokens field = input + cache_read + cache_write.

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_social-account-analyzer_run1/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- platform.llm_model: your model name (e.g. "Claude Sonnet 4.6")
- phases.install: all null (no install)
- phases.asset_acquisition: all null (no video download)
- phases.execution.steps: [{name:"t1_instagram", duration_s, notes:"fetch_s=X llm_s=Y"}, {name:"t2_x", ...}, {name:"t3_tiktok", ...}]
- phases.delivery.upload_s: 0 (no CDN upload)
- tokens: fill from session stats if available, null otherwise
- cost: calculate from tokens × pricing
- totals: wall_total_s, tool_calls_s, llm_overhead_s (wall - tools), llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Managed Claude Agent Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the social-account-analyzer skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/keys/.env` (the `ANTHROPIC_API_KEY` value)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `<TBD — to be filled when MCA environment for SAA is provisioned>`
- Environment ID: `<TBD>`
- The environment needs: PIKA_API_BASE_URL, PIKA_AGENT_API_KEY injected as env vars; nova3-agent-skills repo accessible at /workspace/skills/

## Steps

1. Clean: `rm -f /tmp/bench_mca_saa_* 2>/dev/null`

2. Source the API key and create a session:
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
       \"title\": \"Benchmark: social-account-analyzer $(date +%Y-%m-%d_%H%M)\"
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
         "content": [{"type": "text", "text": "Run the social-account-analyzer skill on 3 accounts. For each, record the start time, run the skill, record the end time, and print the timing.\n\nPrepend your ENVIRONMENT SETUP exports (PIKA_AGENT_API_KEY, PIKA_API_BASE_URL, PYTHONPATH) to every python command.\n\nT1 — Instagram @natgeo:\n```bash\nT_START=$(date +%s%N)\npython3 /workspace/skills/social-account-analyzer/scripts/analyze_account.py analyze \"@natgeo\" --platform instagram > /tmp/bench_t1_out.json 2>/tmp/bench_t1_err.txt\nT_END=$(date +%s%N)\necho \"T1_instagram_ms: $(( (T_END - T_START) / 1000000 ))\"\ngrep -E \"⏱️|fetch|llm|Error\" /tmp/bench_t1_err.txt\ncat /tmp/bench_t1_out.json | python3 -c \"import json,sys; d=json.load(sys.stdin); p=d.get('profile',{}); print(f'success={d.get(\\\"success\\\")} handle={p.get(\\\"handle\\\")} followers={p.get(\\\"followers\\\")}')\"\n```\n\nT2 — X/Twitter @NASA:\n```bash\nT_START=$(date +%s%N)\npython3 /workspace/skills/social-account-analyzer/scripts/analyze_account.py analyze \"@NASA\" --platform x > /tmp/bench_t2_out.json 2>/tmp/bench_t2_err.txt\nT_END=$(date +%s%N)\necho \"T2_x_ms: $(( (T_END - T_START) / 1000000 ))\"\ngrep -E \"⏱️|fetch|llm|Error\" /tmp/bench_t2_err.txt\ncat /tmp/bench_t2_out.json | python3 -c \"import json,sys; d=json.load(sys.stdin); p=d.get('profile',{}); print(f'success={d.get(\\\"success\\\")} handle={p.get(\\\"handle\\\")} followers={p.get(\\\"followers\\\")}')\"\n```\n\nT3 — TikTok @khaby.lame:\n```bash\nT_START=$(date +%s%N)\npython3 /workspace/skills/social-account-analyzer/scripts/analyze_account.py analyze \"@khaby.lame\" --platform tiktok > /tmp/bench_t3_out.json 2>/tmp/bench_t3_err.txt\nT_END=$(date +%s%N)\necho \"T3_tiktok_ms: $(( (T_END - T_START) / 1000000 ))\"\ngrep -E \"⏱️|fetch|llm|Error\" /tmp/bench_t3_err.txt\ncat /tmp/bench_t3_out.json | python3 -c \"import json,sys; d=json.load(sys.stdin); p=d.get('profile',{}); print(f'success={d.get(\\\"success\\\")} handle={p.get(\\\"handle\\\")} followers={p.get(\\\"followers\\\")}')\"\n```\n\nReport all timing values (T1/T2/T3 ms) and the per-stage breakdown from stderr (fetch_ms, llm_ms)."}]
       }]
     }'
   ```

4. Poll session status every 5s until `status` is `idle` or `terminated` (timeout after 5 min):
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
     if [ $(( $(date +%s) - POLL_START )) -gt 300 ]; then echo "TIMEOUT after 5min"; break; fi
     sleep 5
   done
   ```

5. Record wall end and fetch session metadata:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_saa_session.json | python3 -m json.tool
   ```

6. Fetch events and extract timing:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_saa_events.json \
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

From `/tmp/bench_mca_saa_session.json`:
```bash
python3 -c "
import json
with open('/tmp/bench_mca_saa_session.json') as f:
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

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_social-account-analyzer_runN/result.json

Key values:
- platform.name: "managed-claude-agent"
- platform.runtime: "Anthropic managed container"
- phases.install: all null (deps pre-loaded in environment)
- phases.asset_acquisition: all null
- phases.execution.steps: [{name:"t1_instagram",...}, {name:"t2_x",...}, {name:"t3_tiktok",...}]
- phases.delivery.upload_s: 0

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`
````

---

## Codex Prompt

Start a Codex session. Send this prompt:

````
Run a full e2e performance benchmark of the social-account-analyzer skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/social-account-analyzer/
- Script: ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- No install step, no video download

## Steps

1. Clean:
   ```bash
   rm -f /tmp/bench_saa_* 2>/dev/null
   ```

2. Source API keys and record wall start:
   ```bash
   source ~/keys/.env
   WALL_START=$(date +%s%N)
   echo "WALL_START=$WALL_START"
   ```

3. T1 — Instagram @natgeo:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@natgeo" --platform instagram \
     > /tmp/bench_saa_t1_stdout.txt 2>/tmp/bench_saa_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_instagram: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t1_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t1_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t1_stdout.txt').read()[:300])
   "
   ```

4. T2 — X/Twitter @NASA:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@NASA" --platform x \
     > /tmp/bench_saa_t2_stdout.txt 2>/tmp/bench_saa_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_x: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t2_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t2_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t2_stdout.txt').read()[:300])
   "
   ```

5. T3 — TikTok @khaby.lame:
   ```bash
   T=$(date +%s%N)
   python3 ~/code/nova3-agent-skills/social-account-analyzer/scripts/analyze_account.py \
     analyze "@khaby.lame" --platform tiktok \
     > /tmp/bench_saa_t3_stdout.txt 2>/tmp/bench_saa_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_tiktok: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   grep -E "⏱️|fetch|llm|total|Error" /tmp/bench_saa_t3_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_saa_t3_stdout.txt'))
       p = d.get('profile', {}); perf = d.get('performance', {})
       print(f'success={d.get(\"success\")} handle={p.get(\"handle\")} followers={p.get(\"followers\")} eng={perf.get(\"avg_engagement_rate\")}%')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_saa_t3_stdout.txt').read()[:300])
   "
   ```

6. Record wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_social-account-analyzer_run1/result.json

Key values:
- platform.name: "codex"
- platform.runtime: "Codex sandbox"
- phases.install: all null
- phases.asset_acquisition: all null
- phases.execution.steps: [{name:"t1_instagram",...}, {name:"t2_x",...}, {name:"t3_tiktok",...}]
- phases.delivery.upload_s: 0

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **No video input / no CDN upload:** SAA is API+LLM only — `phases.asset_acquisition` and `phases.delivery.upload_s` are always null/0.
- **Per-stage timing from stderr:** Each test case logs `⏱️ [fetch] Xs` and `⏱️ [llm] Xs` to stderr. Always capture full stderr (`2>/tmp/bench_saa_tN_stderr.txt`) and grep for these lines.
- **LLM truncation (known issue in v1.0.7):** SAA pass-2 LLM output may be truncated and auto-repaired. Watch for `⚠️ truncated` in stderr — note if triggered in `meta.notes`.
- **X/Twitter reliability:** X RapidAPI may return 0 posts intermittently — if T2 returns empty data, note in `meta.notes` and consider a retry.
- **Managed Claude Agent:** Agent ID and Environment ID are TBD — fill in once an SAA-compatible MCA environment is provisioned.
- **API key location (devbox):** `~/keys/.env` contains `PIKA_API_BASE_URL` and `PIKA_AGENT_API_KEY`.

## Processing PikaBot Results

When PikaBot sends back the result JSON (as a CDN URL or pasted text):

1. **Download the JSON** (if CDN URL):
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_saa_result.json
   ```

2. **Create the run directory and save**:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_social-account-analyzer_runN
   mkdir -p "$RUN_DIR"
   cp /tmp/pikabot_saa_result.json "$RUN_DIR/result.json"
   ```

3. **Validate**:
   ```bash
   python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py "$RUN_DIR"
   ```
