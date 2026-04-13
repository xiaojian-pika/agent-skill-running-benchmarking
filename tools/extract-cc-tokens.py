#!/usr/bin/env python3
"""Extract token usage from a Claude Code session JSONL file.

Usage:
  python3 extract-cc-tokens.py <session-id>
  python3 extract-cc-tokens.py <path-to-jsonl>
  python3 extract-cc-tokens.py --latest

Task isolation (recommended):
  python3 extract-cc-tokens.py --latest --after 2026-04-10T06:00:00 --before 2026-04-10T06:05:00
  python3 extract-cc-tokens.py --latest --after 1775789000000  (epoch ms)

Searches ~/.claude/projects/*/ for session JSONL files.
Prints token counts and estimated cost.

NOTE on Claude API usage fields:
  - input_tokens: only the non-cached portion of input (often near-zero with caching)
  - cache_read_input_tokens: input tokens served from cache (the bulk of input cost)
  - cache_creation_input_tokens: input tokens written to cache
  - Total effective input = input_tokens + cache_read + cache_write
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Pricing per million tokens (2026-04)
PRICING = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
}


def parse_time_filter(val: str) -> Optional[datetime]:
    """Parse a timestamp filter — ISO 8601 or epoch milliseconds."""
    if not val:
        return None
    # Epoch milliseconds
    try:
        epoch_ms = int(val)
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    except ValueError:
        pass
    # ISO 8601
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError:
        pass
    return None


def find_session_jsonl(session_id: str) -> Optional[str]:
    """Find a JSONL file by session ID."""
    claude_dir = Path.home() / ".claude" / "projects"
    for jsonl in claude_dir.rglob("*.jsonl"):
        if session_id in jsonl.name:
            return str(jsonl)
    return None


def find_latest_jsonl() -> Optional[str]:
    """Find the most recently modified session JSONL."""
    claude_dir = Path.home() / ".claude" / "projects"
    jsonls = sorted(claude_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for j in jsonls:
        if "subagent" not in str(j):
            return str(j)
    return None


def extract_tokens(jsonl_path: str, after: Optional[datetime] = None, before: Optional[datetime] = None) -> dict:
    """Extract token totals from a session JSONL, optionally filtered by timestamp range."""
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    model = None
    session_id = None
    msg_count = 0
    filtered_count = 0

    with open(jsonl_path) as f:
        for line in f:
            try:
                d = json.loads(line)
                if not session_id:
                    session_id = d.get("sessionId", "")
                usage = d.get("message", {}).get("usage", {})
                if not usage:
                    continue

                # Timestamp filtering
                if after or before:
                    ts_str = d.get("timestamp", "")
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if after and ts < after:
                                filtered_count += 1
                                continue
                            if before and ts > before:
                                filtered_count += 1
                                continue
                        except ValueError:
                            pass

                if not model:
                    model = d.get("message", {}).get("model", "")
                for k in totals:
                    totals[k] += usage.get(k, 0)
                msg_count += 1
            except (json.JSONDecodeError, AttributeError):
                pass

    effective_input = totals["input_tokens"] + totals["cache_read_input_tokens"] + totals["cache_creation_input_tokens"]

    return {
        "path": jsonl_path,
        "session_id": session_id,
        "model": model,
        "messages": msg_count,
        "filtered_out": filtered_count,
        **totals,
        "effective_input_tokens": effective_input,
        "total_tokens": sum(totals.values()),
    }


def estimate_cost(data: dict) -> Optional[float]:
    """Estimate USD cost from token counts and model."""
    model = data.get("model", "")
    prices = PRICING.get(model)
    if not prices:
        return None
    return (
        data["input_tokens"] * prices["input"]
        + data["output_tokens"] * prices["output"]
        + data["cache_creation_input_tokens"] * prices["cache_write"]
        + data["cache_read_input_tokens"] * prices["cache_read"]
    ) / 1_000_000


def parse_args():
    """Parse CLI arguments."""
    args = {"target": None, "after": None, "before": None, "json_out": False}
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--after" and i + 1 < len(sys.argv):
            args["after"] = sys.argv[i + 1]
            i += 2
        elif a == "--before" and i + 1 < len(sys.argv):
            args["before"] = sys.argv[i + 1]
            i += 2
        elif a == "--json":
            args["json_out"] = True
            i += 1
        elif a == "--latest":
            args["target"] = "--latest"
            i += 1
        elif not a.startswith("--"):
            args["target"] = a
            i += 1
        else:
            i += 1
    return args


def main():
    args = parse_args()

    if not args["target"]:
        print("Usage: python3 extract-cc-tokens.py <session-id|path|--latest> [--after TS] [--before TS] [--json]")
        print("")
        print("Task isolation: use --after/--before to filter by timestamp range.")
        print("  TS can be ISO 8601 (2026-04-10T06:00:00) or epoch milliseconds.")
        sys.exit(1)

    target = args["target"]
    if target == "--latest":
        path = find_latest_jsonl()
    elif os.path.isfile(target):
        path = target
    else:
        path = find_session_jsonl(target)

    if not path:
        print(f"Error: session not found: {target}")
        sys.exit(1)

    after = parse_time_filter(args["after"]) if args["after"] else None
    before = parse_time_filter(args["before"]) if args["before"] else None

    data = extract_tokens(path, after=after, before=before)
    cost = estimate_cost(data)

    if not args["json_out"]:
        print(f"Session: {data['session_id']}")
        print(f"Model:   {data['model']}")
        print(f"File:    {data['path']}")
        print(f"Messages with usage: {data['messages']}")
        if data["filtered_out"]:
            print(f"Messages filtered out: {data['filtered_out']}")
        if after or before:
            print(f"Time filter: after={args['after']} before={args['before']}")
        print()
        print(f"  input_tokens (non-cached): {data['input_tokens']:>10,}")
        print(f"  cache_write_tokens:        {data['cache_creation_input_tokens']:>10,}")
        print(f"  cache_read_tokens:         {data['cache_read_input_tokens']:>10,}")
        print(f"  effective_input_tokens:     {data['effective_input_tokens']:>10,}  (input + cache_read + cache_write)")
        print(f"  output_tokens:             {data['output_tokens']:>10,}")
        print(f"  total_tokens:              {data['total_tokens']:>10,}")
        print()
        if cost is not None:
            print(f"  Estimated cost:            ${cost:.4f}")
        else:
            print(f"  Estimated cost:            unknown (model '{data['model']}' not in pricing table)")

    if args["json_out"]:
        print(json.dumps({
            "input_tokens": data["input_tokens"],
            "output_tokens": data["output_tokens"],
            "cache_read_tokens": data["cache_read_input_tokens"],
            "cache_write_tokens": data["cache_creation_input_tokens"],
            "effective_input_tokens": data["effective_input_tokens"],
            "total_tokens": data["total_tokens"],
            "estimated_cost_usd": round(cost, 4) if cost is not None else None,
            "model": data["model"],
            "messages": data["messages"],
            "filtered_out": data["filtered_out"],
        }, indent=2))


if __name__ == "__main__":
    main()
