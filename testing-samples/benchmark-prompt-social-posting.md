# Benchmark Prompt: social-posting

> **Skill:** social-posting
> **Test cases:** T1 X caption, T2 Instagram caption, T3 TikTok caption (funny), T4 Instagram ×3 variations
> **Content brief:** "video tutorial: how to cook perfect pasta at home — tested 5 different techniques"
> **Expected output:** JSON with caption + hashtags + full_post per test case
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the social-posting skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Generate captions for this content brief on 4 test cases:
- T1: `--content "video tutorial: how to cook perfect pasta at home — tested 5 different techniques" --platform x --tone casual`
- T2: same content, `--platform instagram --tone casual`
- T3: same content, `--platform tiktok --tone funny`
- T4: same content, `--platform instagram --tone casual --variations 3`

## Steps

1. Clean: `rm -f /tmp/bench_sp_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"`
3. Install skill "social-posting" from Pika Staging Skill Hub (CMS). Time each sub-step (cms_fetch, skill_install, subagent_start).
4. Run T1, T2, T3, T4 in sequence. Time each one individually.
   - Capture full stderr for each run (contains `⏱️ [llm] Xs` and `⏱️ [total] Xs` timing lines).
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`

## Timing rules

- Time EVERY step with `T=$(date +%s%N)` before and `$(( ($(date +%s%N) - T) / 1000000 ))ms` after
- LLM call time per test case comes from stderr: `⏱️ [llm] Xs`; overhead = skill_run_total - llm
- LLM overhead (agent thinking) = WALL_TOTAL - sum of all tool call times
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

1. Save the complete filled-in JSON to `/tmp/bench_sp_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input.name="pasta-tutorial-brief", test_input.description="video tutorial: how to cook perfect pasta..."
- task: name="social-posting", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.asset_acquisition: all null (pure LLM skill, no downloads)
- phases.execution.steps: 4 entries:
  - {name:"t1_x_casual", duration_s, notes:"llm_s=X (from stderr ⏱️ [llm]) caption_len=N hashtags=N"}
  - {name:"t2_instagram_casual", duration_s, notes:"llm_s=X caption_len=N hashtags_count=N"}
  - {name:"t3_tiktok_funny", duration_s, notes:"llm_s=X caption_len=N"}
  - {name:"t4_instagram_variations3", duration_s, notes:"llm_s=X variations_returned=N (expected 3)"}
- phases.delivery: upload_s for result JSON, output_url = CDN URL of result JSON
- totals: wall_total_s, tool_calls_s, llm_overhead_s, llm_pct, skill_pct
- tokens and cost: from session JSONL parsing

Note any `⚠️` warnings in stderr (e.g. hashtag format issues, variations truncation).

Do NOT skip any fields. Use null for values you genuinely can't measure.
```

---

## Claude Code Prompt

Start a new Claude Code session (e.g. `claude --model sonnet` for Sonnet). Send this prompt:

````
Run a full e2e performance benchmark of the social-posting skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/social-posting/
- Script: ~/code/nova3-agent-skills/social-posting/scripts/generate_caption.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- No install step. No ffmpeg/yt-dlp needed.

## Steps

1. Source API keys and record wall start:
   ```bash
   source ~/keys/.env
   rm -f /tmp/bench_sp_* 2>/dev/null
   WALL_START=$(date +%s%N)
   echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/social-posting/scripts/generate_caption.py
   CONTENT="video tutorial: how to cook perfect pasta at home — tested 5 different techniques"
   ```

2. T1 — X/Twitter, tone=casual:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform x --tone casual \
     > /tmp/bench_sp_t1_stdout.txt 2>/tmp/bench_sp_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_x_casual: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_sp_t1_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_sp_t1_stdout.txt'))
       cap = d.get('caption',''); tags = d.get('hashtags',[])
       print(f'caption_len={len(cap)} hashtags={tags}')
       print(f'full_post_len={len(d.get(\"full_post\",\"\"))}')
       print(f'preview: {cap[:120]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_sp_t1_stdout.txt').read()[:400])
   "
   ```

3. T2 — Instagram, tone=casual:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform instagram --tone casual \
     > /tmp/bench_sp_t2_stdout.txt 2>/tmp/bench_sp_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_instagram_casual: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr ===" && cat /tmp/bench_sp_t2_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_sp_t2_stdout.txt'))
       cap = d.get('caption',''); tags = d.get('hashtags',[])
       print(f'caption_len={len(cap)} hashtags_count={len(tags)}')
       print(f'preview: {cap[:120]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_sp_t2_stdout.txt').read()[:400])
   "
   ```

4. T3 — TikTok, tone=funny:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform tiktok --tone funny \
     > /tmp/bench_sp_t3_stdout.txt 2>/tmp/bench_sp_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_tiktok_funny: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_sp_t3_stderr.txt
   python3 -c "
   import json
   try:
       d = json.load(open('/tmp/bench_sp_t3_stdout.txt'))
       cap = d.get('caption','')
       print(f'caption_len={len(cap)} hashtags_count={len(d.get(\"hashtags\",[]))}')
       print(f'preview: {cap[:120]}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_sp_t3_stdout.txt').read()[:400])
   "
   ```

5. T4 — Instagram, ×3 variations:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform instagram --tone casual --variations 3 \
     > /tmp/bench_sp_t4_stdout.txt 2>/tmp/bench_sp_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_instagram_variations3: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_sp_t4_stderr.txt
   python3 -c "
   import json
   try:
       data = json.load(open('/tmp/bench_sp_t4_stdout.txt'))
       items = data if isinstance(data, list) else [data]
       print(f'variations_returned={len(items)} (expected 3)')
       for i, v in enumerate(items):
           cap = v.get('caption','')
           print(f'  v{i+1}: caption_len={len(cap)} hashtags_count={len(v.get(\"hashtags\",[]))}')
   except Exception as e:
       print(f'parse error: {e}'); print(open('/tmp/bench_sp_t4_stdout.txt').read()[:400])
   "
   ```

6. Record wall end:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   ```

## Timing notes

- `⏱️ [llm] Xs` in stderr = time for the Anthropic API call inside the skill
- `⏱️ [total] Xs` = total skill script execution time (should match wall time for that test case)
- skill internal overhead = total - llm (JSON parsing, prompt construction, validation)
- Watch for `⚠️` lines in stderr (hashtag format warnings, truncation warnings)

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_social-posting_run1/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- phases.install: all null (no install)
- phases.asset_acquisition: all null (pure LLM, no downloads)
- phases.execution.steps:
  - {name:"t1_x_casual", duration_s, notes:"llm_s=X caption_len=N hashtags=N"}
  - {name:"t2_instagram_casual", duration_s, notes:"llm_s=X caption_len=N hashtags_count=N"}
  - {name:"t3_tiktok_funny", duration_s, notes:"llm_s=X caption_len=N"}
  - {name:"t4_instagram_variations3", duration_s, notes:"llm_s=X variations_returned=N"}
- phases.delivery.upload_s: 0 (no CDN upload)
- tokens: fill from session stats
- totals: wall_total_s, tool_calls_s, llm_overhead_s (wall - tools), llm_pct, skill_pct

Note: `tool_calls_s` for this skill is almost entirely LLM calls (T1+T2+T3+T4 Anthropic calls). The `llm_overhead_s` here captures the *agent* thinking time between steps, not the skill's internal LLM calls.

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Managed Claude Agent Prompt

Start a new Claude Code session. Send this prompt:

````
Run a full e2e performance benchmark of the social-posting skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/keys/.env` (ANTHROPIC_API_KEY)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `<TBD — to be filled when MCA environment for SP is provisioned>`
- Environment ID: `<TBD>`
- The environment needs: PIKA_API_BASE_URL, PIKA_AGENT_API_KEY injected; nova3-agent-skills at /workspace/skills/
- No heavy deps needed (pure Python + requests). No ffmpeg, no yt-dlp. No bash timeout risk.

## Steps

1. Clean: `rm -f /tmp/bench_mca_sp_* 2>/dev/null`

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
       \"title\": \"Benchmark: social-posting $(date +%Y-%m-%d_%H%M)\"
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
         "content": [{"type": "text", "text": "Run 4 caption generation tests using the social-posting skill. Prepend your ENVIRONMENT SETUP exports to every python command.\n\nSKILL_SCRIPT=/workspace/skills/social-posting/scripts/generate_caption.py\nCONTENT=\"video tutorial: how to cook perfect pasta at home — tested 5 different techniques\"\n\nT1 — X/Twitter casual:\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT --content \"$CONTENT\" --platform x --tone casual > /tmp/t1_out.json 2>/tmp/t1_err.txt\nT_END=$(date +%s%N)\necho \"T1_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t1_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t1_out.json')); print(f'caption_len={len(d.get(\\\"caption\\\",\\\"\\\"))} hashtags={d.get(\\\"hashtags\\\",[])}'); print(d.get('caption','')[:120])\"\n```\n\nT2 — Instagram casual:\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT --content \"$CONTENT\" --platform instagram --tone casual > /tmp/t2_out.json 2>/tmp/t2_err.txt\nT_END=$(date +%s%N)\necho \"T2_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t2_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t2_out.json')); print(f'caption_len={len(d.get(\\\"caption\\\",\\\"\\\"))} hashtags_count={len(d.get(\\\"hashtags\\\",[]))}')\"\n```\n\nT3 — TikTok funny:\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT --content \"$CONTENT\" --platform tiktok --tone funny > /tmp/t3_out.json 2>/tmp/t3_err.txt\nT_END=$(date +%s%N)\necho \"T3_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t3_err.txt\npython3 -c \"import json; d=json.load(open('/tmp/t3_out.json')); print(f'caption_len={len(d.get(\\\"caption\\\",\\\"\\\"))}'); print(d.get('caption','')[:120])\"\n```\n\nT4 — Instagram ×3 variations:\n```bash\nT_START=$(date +%s%N)\npython3 $SKILL_SCRIPT --content \"$CONTENT\" --platform instagram --tone casual --variations 3 > /tmp/t4_out.json 2>/tmp/t4_err.txt\nT_END=$(date +%s%N)\necho \"T4_ms: $(( (T_END - T_START) / 1000000 ))\"\ncat /tmp/t4_err.txt\npython3 -c \"import json; data=json.load(open('/tmp/t4_out.json')); items=data if isinstance(data,list) else [data]; print(f'variations_returned={len(items)} (expected 3)'); [print(f'  v{i+1}: caption_len={len(v.get(\\\"caption\\\",\\\"\\\"))} hashtags_count={len(v.get(\\\"hashtags\\\",[]))}') for i,v in enumerate(items)]\"\n```\n\nReport T1/T2/T3/T4 timings, result sizes, and any ⚠️ warnings from stderr."}]
       }]
     }'
   ```

4. Poll session status every 5s until `idle` or `terminated` (timeout 5 min):
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

5. Record wall end and fetch metadata:
   ```bash
   WALL_END=$(date +%s%N)
   echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_sp_session.json | python3 -m json.tool
   ```

6. Fetch events and extract timing:
   ```bash
   curl -sS "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     | tee /tmp/bench_mca_sp_events.json \
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
with open('/tmp/bench_mca_sp_session.json') as f:
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
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_social-posting_runN/result.json

Key values:
- platform.name: "managed-claude-agent"
- phases.install, phases.asset_acquisition: null
- phases.execution.steps: 4 entries (t1_x_casual, t2_instagram_casual, t3_tiktok_funny, t4_instagram_variations3)
- phases.delivery.upload_s: 0

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`
````

---

## Codex Prompt

Start a Codex session. Send this prompt:

````
Run a full e2e performance benchmark of the social-posting skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/social-posting/
- Script: ~/code/nova3-agent-skills/social-posting/scripts/generate_caption.py
- API keys: source from `~/keys/.env` (PIKA_API_BASE_URL, PIKA_AGENT_API_KEY)
- No install step. No heavy deps needed.

## Steps

1. Source keys and wall start:
   ```bash
   source ~/keys/.env
   rm -f /tmp/bench_sp_* 2>/dev/null
   WALL_START=$(date +%s%N); echo "WALL_START=$WALL_START"
   SKILL_SCRIPT=~/code/nova3-agent-skills/social-posting/scripts/generate_caption.py
   CONTENT="video tutorial: how to cook perfect pasta at home — tested 5 different techniques"
   ```

2. T1 — X/Twitter casual:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform x --tone casual \
     > /tmp/bench_sp_t1_stdout.txt 2>/tmp/bench_sp_t1_stderr.txt
   EXIT_T1=$?
   echo "T1_x_casual: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T1"
   echo "=== T1 stderr ===" && cat /tmp/bench_sp_t1_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_sp_t1_stdout.txt'))
   print(f'caption_len={len(d.get(\"caption\",\"\"))} hashtags={d.get(\"hashtags\",[])}')
   print(d.get('caption','')[:120])
   "
   ```

3. T2 — Instagram casual:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform instagram --tone casual \
     > /tmp/bench_sp_t2_stdout.txt 2>/tmp/bench_sp_t2_stderr.txt
   EXIT_T2=$?
   echo "T2_instagram_casual: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T2"
   echo "=== T2 stderr ===" && cat /tmp/bench_sp_t2_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_sp_t2_stdout.txt'))
   print(f'caption_len={len(d.get(\"caption\",\"\"))} hashtags_count={len(d.get(\"hashtags\",[]))}')
   "
   ```

4. T3 — TikTok funny:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform tiktok --tone funny \
     > /tmp/bench_sp_t3_stdout.txt 2>/tmp/bench_sp_t3_stderr.txt
   EXIT_T3=$?
   echo "T3_tiktok_funny: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T3"
   echo "=== T3 stderr ===" && cat /tmp/bench_sp_t3_stderr.txt
   python3 -c "
   import json
   d=json.load(open('/tmp/bench_sp_t3_stdout.txt'))
   print(f'caption_len={len(d.get(\"caption\",\"\"))} hashtags_count={len(d.get(\"hashtags\",[]))}')
   print(d.get('caption','')[:120])
   "
   ```

5. T4 — Instagram ×3 variations:
   ```bash
   T=$(date +%s%N)
   python3 "$SKILL_SCRIPT" --content "$CONTENT" --platform instagram --tone casual --variations 3 \
     > /tmp/bench_sp_t4_stdout.txt 2>/tmp/bench_sp_t4_stderr.txt
   EXIT_T4=$?
   echo "T4_instagram_variations3: $(( ($(date +%s%N) - T) / 1000000 ))ms  exit=$EXIT_T4"
   echo "=== T4 stderr ===" && cat /tmp/bench_sp_t4_stderr.txt
   python3 -c "
   import json
   data=json.load(open('/tmp/bench_sp_t4_stdout.txt'))
   items=data if isinstance(data,list) else [data]
   print(f'variations_returned={len(items)} (expected 3)')
   for i,v in enumerate(items):
       print(f'  v{i+1}: caption_len={len(v.get(\"caption\",\"\"))} hashtags_count={len(v.get(\"hashtags\",[]))}')
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
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_social-posting_run1/result.json

Key values:
- platform.name: "codex"
- phases.install, phases.asset_acquisition: null
- phases.execution.steps: 4 entries (t1_x_casual, t2_instagram_casual, t3_tiktok_funny, t4_instagram_variations3)
- phases.delivery.upload_s: 0
- In each step's notes: `llm_s=X` (from stderr `⏱️ [llm]`), result metadata

Validate: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py <dir>`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **Pure LLM skill:** social-posting makes a single Anthropic API call per invocation. `phases.asset_acquisition` = null. `phases.delivery.upload_s` = 0 for all platforms.
- **Stderr timing:** Each run logs `⏱️ [llm] Xs` (Anthropic call time) and `⏱️ [total] Xs`. Record `llm_s` per step from stderr; `overhead_s = total_s - llm_s` (JSON parsing, prompt construction, validation).
- **T4 variations fix (v1.0.6+):** `--variations 3` now dynamically scales `max_tokens = max(1200, n×500+200)` to prevent JSON truncation. If only 1 variation is returned on v1.0.6+, it's a regression — note in meta.notes.
- **Hashtag format (known issue):** Hashtags in the JSON array may sometimes lack `#` prefix (~25% of runs on older versions). `full_post` field always includes the `#` prefix correctly. Record if triggered via `⚠️` lines in stderr.
- **Managed Claude Agent:** Agent ID and Environment ID are TBD — fill in once an SP-compatible MCA environment is provisioned.
- **API key location (devbox):** `~/keys/.env` contains PIKA_API_BASE_URL and PIKA_AGENT_API_KEY.

## Processing PikaBot Results

When PikaBot sends back the result JSON (CDN URL or pasted):

1. Download:
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_sp_result.json
   ```

2. Save to run dir:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_social-posting_runN
   mkdir -p "$RUN_DIR" && cp /tmp/pikabot_sp_result.json "$RUN_DIR/result.json"
   ```

3. Validate:
   ```bash
   python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py "$RUN_DIR"
   ```
