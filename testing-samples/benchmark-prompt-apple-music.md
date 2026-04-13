# Benchmark Prompt: apple-music-reference

> **Skill:** apple-music-reference
> **Test query:** "bohemian rhapsody queen"
> **Expected output:** 30-second M4A preview of Bohemian Rhapsody by Queen
> **Platforms:** PikaBot, Claude Code, Managed Claude Agent, Codex

---

## PikaBot Prompt

Send this to PikaBot along with `templates/benchmark-run.json` and `templates/recording-guide.md`:

```
Run a full e2e performance benchmark of the apple-music-reference skill. I've sent you the JSON template (benchmark-run.json) and recording guide (recording-guide.md) — fill in the JSON with your actual measured values.

## What to benchmark

Search Apple Music for "bohemian rhapsody queen" and download the 30-second preview.

## Steps

1. Clean: `rm -f /tmp/bench_am_* 2>/dev/null`
3. Record wall start: `echo "WALL_START=$(date +%s%N)"`
4. Install skill "apple-music-reference" from Pika Staging Skill Hub. Time each sub-step:
   a. GET `https://skills-cms.pika-labs.app/api/hub/install?id=apple-music-reference` → response has `bundleUrl` and `version`
   b. If `/data/.pikabot/workspace/skills/apple-music-reference/SKILL.md` exists, remove the old folder first (this is an upgrade)
   c. Download zip from `bundleUrl`, extract to `/data/.pikabot/workspace/skills/apple-music-reference/` (SKILL.md must be at root — flatten if nested in subfolder)
   d. Create a subagent to start a new session. The installed skill will be available for use.
5. Run each stage individually and time it:
   - Search only: `python3 $PIKABOT_SKILLS_DIR/apple-music-reference/scripts/apple_music.py --search-only "bohemian rhapsody queen"`
   - Search + download: `python3 $PIKABOT_SKILLS_DIR/apple-music-reference/scripts/apple_music.py "bohemian rhapsody queen" /tmp/bench_am_preview.m4a`
6. Upload output to CDN using `pika-upload-file`. Time it.
7. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - WALL_START) / 1000000 ))ms"`


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

1. Save the complete filled-in JSON to `/tmp/bench_am_result.json`
2. Upload it using `pika-upload-file` and get the CDN URL
3. Reply to me with: the CDN URL of the JSON file, the wall_total_s, tool_calls_s, llm_pct, and a brief summary of observations

Do all 3 steps — especially step 3. If the upload fails, paste the JSON directly in your reply instead.

Key fields:
- meta: date, tester="pikabot", test_input is N/A (no video input, just a search query)
- task: name="apple-music-reference", version from CMS
- platform: name="pikabot", runtime="EKS pod", llm_model
- phases.execution.steps: search_apple_music, search_and_download_preview
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
Run a full e2e performance benchmark of the apple-music-reference skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/apple-music-reference/
- Python: ~/.venvs/captions/bin/python (has httpx installed)
- Env vars needed: PYTHONPATH=/home/mingzhi/code/nova3-agent-skills, PIKA_API_BASE_URL, PIKA_AGENT_API_KEY
- Use mingzhi's staging fallback: PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art, PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o
- No install step, no upload step, no video download

## Steps

1. Clean: `rm -f /tmp/bench_am_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"` — note the nanosecond value
3. Search only:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/apple-music-reference/scripts/apple_music.py \
     --search-only "bohemian rhapsody queen" > /tmp/bench_am_search.json 2>/tmp/bench_am_search_log.txt
   echo "search_apple_music: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   cat /tmp/bench_am_search_log.txt
   ```
4. Search + download preview:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/apple-music-reference/scripts/apple_music.py \
     "bohemian rhapsody queen" /tmp/bench_am_preview.m4a 2>/tmp/bench_am_dl_log.txt
   echo "search_and_download: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   cat /tmp/bench_am_dl_log.txt
   echo "preview_size: $(du -k /tmp/bench_am_preview.m4a | cut -f1) KB"
   ```
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - <WALL_START_VALUE>) / 1000000 ))ms"` — substitute the nanosecond value from step 2

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-cc-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Replace `<WALL_START_ISO>` and `<WALL_END_ISO>` with the ISO timestamps (or epoch ms) from your wall start/end steps. The `--after`/`--before` flags isolate tokens to this benchmark task only (important if the session has other work).

This outputs input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, effective_input_tokens, total_tokens, and estimated_cost_usd. Note: with Claude caching, most input tokens appear in cache_read_tokens, not input_tokens. The effective_input_tokens field = input + cache_read + cache_write.

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_claudecode_<model>_apple-music_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- task.name: "apple-music-reference"
- platform.name: "claudecode"
- platform.runtime: "staging devbox"
- platform.llm_model: your model name (e.g. "Claude Sonnet 4.6")
- phases.install: all null (no install)
- phases.asset_acquisition: all null (no video download)
- phases.delivery.upload_s: 0 (no upload)
- phases.execution.steps: search_apple_music, search_and_download_preview
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
Run a full e2e performance benchmark of the apple-music-reference skill via a Claude Managed Agent. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

You will orchestrate a managed agent session via the Anthropic API, time everything, extract results, and save the benchmark JSON.

## Setup
- API key: source from `~/code/internal-prototyping/keys/.env` (the `ANTHROPIC_API_KEY` value)
- API base: https://api.anthropic.com/v1
- Beta header: `anthropic-beta: managed-agents-2026-04-01`
- Agent ID: `agent_011CZuSXCsdKcAXr72fDutTF` (pika-apple-music)
- Environment ID: `env_01DFeEoMP4TH1q55w725r3ys` (pika-media-env, has httpx + requests)
- The agent's system prompt has PIKA_API_BASE_URL and PIKA_AGENT_API_KEY in its ENVIRONMENT SETUP block
- **Fair comparison:** Other platforms (Claude Code, Codex) have dependencies pre-installed. Do NOT count dependency install or environment setup time in the benchmark. If the container is cold, pre-warm it in a throwaway session before starting the timed run.
- This is a fast, pure-API skill — no nohup needed (completes well within 295s bash timeout)

## Steps

1. Clean: `rm -f /tmp/bench_mca_* 2>/dev/null`

2. Source the API key, record wall start, and create a session:
   ```bash
   export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/code/internal-prototyping/keys/.env | cut -d= -f2)
   AGENT_ID="agent_011CZuSXCsdKcAXr72fDutTF"
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
       \"title\": \"Benchmark: apple-music $(date +%Y-%m-%d_%H%M)\"
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
         "content": [{"type": "text", "text": "Search Apple Music for \"bohemian rhapsody queen\" and download the 30-second preview.\n\nPrepend your ENVIRONMENT SETUP exports (PIKA_AGENT_API_KEY, PIKA_API_BASE_URL, PYTHONPATH, nova3_common symlink) to every bash command that runs Python scripts.\n\nFollow these steps exactly, timing each one:\n\n## Step 1: Search only\n```bash\nT_START=$(date +%s%N)\npython /workspace/skills/apple-music-reference/scripts/apple_music.py --search-only \"bohemian rhapsody queen\"\nT_END=$(date +%s%N)\necho \"search_ms: $(( (T_END - T_START) / 1000000 ))\"\n```\n\n## Step 2: Search + download preview\n```bash\nT_START=$(date +%s%N)\npython /workspace/skills/apple-music-reference/scripts/apple_music.py \"bohemian rhapsody queen\" /mnt/session/outputs/preview.m4a\nT_END=$(date +%s%N)\necho \"search_and_download_ms: $(( (T_END - T_START) / 1000000 ))\"\necho \"preview_size_kb: $(du -k /mnt/session/outputs/preview.m4a | cut -f1)\"\n```\n\n## Step 3: Upload to CDN\n```bash\nT_START=$(date +%s%N)\npython3 -c \"\nimport sys; sys.path.insert(0, '/workspace/skills')\nfrom nova3_common.cdn import upload_to_cdn\nfrom nova3_common.config import get_proxy_config\nbase_url, api_key = get_proxy_config()\nurl = upload_to_cdn('/mnt/session/outputs/preview.m4a', base_url, api_key)\nprint(f'CDN_URL: {url}')\n\"\nT_END=$(date +%s%N)\necho \"upload_ms: $(( (T_END - T_START) / 1000000 ))\"\n```\n\nReport all timing values and the CDN URL."}]
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
     ACTIVE=$(echo "$STATUS" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('stats',{}).get('active_seconds',0))")
     echo "$(date +%T) status=$STATE active=${ACTIVE}s"
     if [ "$STATE" = "idle" ] || [ "$STATE" = "terminated" ]; then break; fi
     if [ $(( $(date +%s) - POLL_START )) -gt 300 ]; then echo "TIMEOUT after 5min"; break; fi
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
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_managed-claude-agent_<model>_apple-music_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- platform.name: "managed-claude-agent"
- platform.runtime: "Anthropic managed container"
- platform.llm_model: from session metadata (e.g. "Claude Sonnet 4.6")
- phases.install: all null (environment has deps pre-loaded via init_script)
- phases.asset_acquisition: all null (no video download)
- phases.execution.steps: map tool calls by command content (apple_music.py --search-only=search, apple_music.py with output=download, upload_to_cdn=delivery)
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
Run a full e2e performance benchmark of the apple-music-reference skill. First read these two files:
- ~/code/agent-skill-running-benchmarking/templates/benchmark-run.json (output format)
- ~/code/agent-skill-running-benchmarking/templates/recording-guide.md (how to fill fields)

Fill in the JSON template with your actual measured values.

## Setup
- Skill location: ~/code/nova3-agent-skills/apple-music-reference/
- Python: ~/.venvs/captions/bin/python (has httpx installed)
- Env vars needed: PYTHONPATH=/home/mingzhi/code/nova3-agent-skills, PIKA_API_BASE_URL, PIKA_AGENT_API_KEY
- Use mingzhi's staging fallback: PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art, PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o
- No install step, no upload step, no video download

## Steps

1. Clean: `rm -f /tmp/bench_am_* 2>/dev/null`
2. Record wall start: `echo "WALL_START=$(date +%s%N)"` — note the nanosecond value
3. Search only:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/apple-music-reference/scripts/apple_music.py \
     --search-only "bohemian rhapsody queen" > /tmp/bench_am_search.json 2>/tmp/bench_am_search_log.txt
   echo "search_apple_music: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   cat /tmp/bench_am_search_log.txt
   ```
4. Search + download preview:
   ```bash
   T=$(date +%s%N)
   PYTHONPATH=/home/mingzhi/code/nova3-agent-skills \
   PIKA_API_BASE_URL=https://mnbvcxzlkjh9o4p.pika.art \
   PIKA_AGENT_API_KEY=ak_zBO3WUAGn2Hrc5PZhZ5FJN4ubcWSVHCoOtvrsWEsU4o \
   ~/.venvs/captions/bin/python \
     ~/code/nova3-agent-skills/apple-music-reference/scripts/apple_music.py \
     "bohemian rhapsody queen" /tmp/bench_am_preview.m4a 2>/tmp/bench_am_dl_log.txt
   echo "search_and_download: $(( ($(date +%s%N) - T) / 1000000 ))ms"
   cat /tmp/bench_am_dl_log.txt
   echo "preview_size: $(du -k /tmp/bench_am_preview.m4a | cut -f1) KB"
   ```
5. Record wall end: `WALL_END=$(date +%s%N); echo "WALL_TOTAL: $(( (WALL_END - <WALL_START_VALUE>) / 1000000 ))ms"` — substitute the nanosecond value from step 2

## Token tracking

After all steps complete, extract your token usage by running:
```bash
python3 ~/code/agent-skill-running-benchmarking/tools/extract-codex-tokens.py --latest --after <WALL_START_ISO> --before <WALL_END_ISO> --json
```
Replace `<WALL_START_ISO>` and `<WALL_END_ISO>` with the ISO timestamps (or epoch ms) from your wall start/end steps. The `--after`/`--before` flags compute a delta between token snapshots, isolating this task from others in the same session.

This outputs input_tokens, output_tokens, cache_read_tokens, total_tokens, and estimated_cost_usd.

## Output

Fill in the benchmark-run.json template and save to:
~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_codex_<model>_apple-music_runN/result.json

Also write a brief report.md in the same directory.

Key values:
- task.name: "apple-music-reference"
- platform.name: "codex"
- platform.runtime: "Codex sandbox"
- platform.llm_model: your model name (e.g. "GPT-4o")
- phases.install: all null (no install)
- phases.asset_acquisition: all null (no video download)
- phases.delivery.upload_s: 0 (no upload)
- phases.execution.steps: search_apple_music, search_and_download_preview
- tokens: fill from session stats if available, null otherwise
- cost: calculate from tokens × pricing. Include cache_read_price_per_million and cache_write_price_per_million (Sonnet 4.6: 0.30/3.75, GPT-5.4: 1.25/0)
- totals: wall_total_s, tool_calls_s, llm_overhead_s (wall - tools), llm_pct, skill_pct

Validate with: `python3 ~/code/agent-skill-running-benchmarking/tools/validate-run.py ~/code/agent-skill-running-benchmarking/runs/<dir>/`

Do NOT skip any steps. Do NOT combine steps. I need ALL raw numbers.
````

---

## Notes

- **/tmp file disappearance:** /tmp files can disappear between separate tool calls (root cause unknown). Chain download + probe + skill run as a single bash command (&&) to avoid this, while capturing individual timings via T=$(date +%s%N) variables within the same call.

- **Clean caches before each run:** `rm -f /tmp/bench_am_*`
- **This is a pure API skill** — zero CPU work, just HTTP calls to Apple Music search + CDN preview download.
- **Preview file:** ~964KB M4A, 30 seconds.
- **Upload variance:** `pika-upload-file` has shown extreme variance (1.8s to 48s) uncorrelated with file size.
- **No nohup needed on managed agents** — this skill completes in seconds, well within the 295s bash tool timeout.
- **API key:** Source from `~/code/internal-prototyping/keys/.env`. Check it's valid with a test call before starting the benchmark.

## Processing PikaBot Results

When PikaBot sends back the result JSON (as a CDN URL or pasted text):

1. **Download the JSON** (if CDN URL):
   ```bash
   curl -sL "<CDN_URL>" -o /tmp/pikabot_result.json
   ```

2. **Create the run directory and save**:
   ```bash
   RUN_DIR=~/code/agent-skill-running-benchmarking/runs/YYYY-MM-DD_pikabot_sonnet-4.6_apple-music_runN
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
   print(f'# apple-music-reference Benchmark — pikabot / {d[\"platform\"][\"llm_model\"]}')
   print(f'')
   print(f'**Date:** {d[\"meta\"][\"date\"]}')
   print(f'**Platform:** pikabot on {d[\"platform\"][\"runtime\"]}')
   print(f'**Skill:** apple-music-reference {d[\"task\"][\"version\"]}')
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
