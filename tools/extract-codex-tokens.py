#!/usr/bin/env python3
"""Extract token usage from a Codex CLI session JSONL file.

Usage:
  python3 extract-codex-tokens.py <path-to-rollout-jsonl>
  python3 extract-codex-tokens.py --latest

Task isolation (recommended):
  python3 extract-codex-tokens.py --latest --after 2026-04-10T06:00:00 --before 2026-04-10T06:05:00

Codex stores session logs at ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl.
Token usage is in event_msg entries with type=token_count, using total_token_usage
(cumulative across the session).

When --after/--before are provided, this tool computes the DELTA between the
token_count event just before the --after timestamp and the token_count event
at/after the --before timestamp, giving task-level isolation even when multiple
tasks run in the same session.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Pricing per million tokens (2026-04)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.0},
    "gpt-5-codex": {"input": 2.50, "output": 10.0},
    "gpt-5.3-codex": {"input": 2.50, "output": 10.0},
    "gpt-5.4": {"input": 2.50, "output": 10.0},
    "o3": {"input": 2.50, "output": 10.0},
}


def parse_time_filter(val: str) -> Optional[datetime]:
    """Parse a timestamp filter — ISO 8601 or epoch milliseconds."""
    if not val:
        return None
    try:
        epoch_ms = int(val)
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError:
        pass
    return None


def find_latest_rollout() -> Optional[str]:
    """Find the most recently modified Codex rollout JSONL."""
    codex_sessions = Path.home() / ".codex" / "sessions"
    if not codex_sessions.exists():
        return None
    rollouts = sorted(codex_sessions.rglob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(rollouts[0]) if rollouts else None


def extract_tokens(jsonl_path: str, after: Optional[datetime] = None, before: Optional[datetime] = None) -> dict:
    """Extract token counts from a Codex session JSONL.

    Without time filters: returns the final cumulative total_token_usage.
    With time filters: computes delta between the snapshot before --after
    and the snapshot at/after --before for task-level isolation.
    """
    all_snapshots = []  # (timestamp, total_token_usage)
    model = None

    with open(jsonl_path) as f:
        for line in f:
            try:
                d = json.loads(line)
                payload = d.get("payload", {})
                if payload.get("type") == "token_count":
                    info = payload.get("info", {})
                    total = info.get("total_token_usage", {})
                    ts_str = d.get("timestamp", "")
                    ts = None
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        except ValueError:
                            pass
                    if total:
                        all_snapshots.append((ts, total))
                if not model:
                    m = payload.get("model") or d.get("model")
                    if m:
                        model = m
            except (json.JSONDecodeError, AttributeError):
                pass

    if not all_snapshots:
        return {"path": jsonl_path, "model": model, "error": "no token_count events found"}

    if after and before:
        # Both bounds: proper delta between two snapshots
        baseline = {"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
                     "reasoning_output_tokens": 0, "total_tokens": 0}
        for ts, snap in all_snapshots:
            if ts and ts < after:
                baseline = snap
            else:
                break

        endpoint = all_snapshots[-1][1]
        for ts, snap in all_snapshots:
            if ts and ts >= before:
                endpoint = snap
                break

        result = {}
        for k in ["input_tokens", "output_tokens", "cached_input_tokens", "reasoning_output_tokens", "total_tokens"]:
            result[k] = endpoint.get(k, 0) - baseline.get(k, 0)
        mode = "delta"
    elif after or before:
        # Only one bound — warn and use partial scope
        import sys
        bound = "--after" if after else "--before"
        other = "--before" if after else "--after"
        print(f"WARNING: {bound} provided without {other} — delta scope is incomplete. "
              f"Provide both for accurate task isolation.", file=sys.stderr)

        baseline = {"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
                     "reasoning_output_tokens": 0, "total_tokens": 0}
        if after:
            for ts, snap in all_snapshots:
                if ts and ts < after:
                    baseline = snap
                else:
                    break
        endpoint = all_snapshots[-1][1]
        if before:
            for ts, snap in all_snapshots:
                if ts and ts >= before:
                    endpoint = snap
                    break

        result = {}
        for k in ["input_tokens", "output_tokens", "cached_input_tokens", "reasoning_output_tokens", "total_tokens"]:
            result[k] = endpoint.get(k, 0) - baseline.get(k, 0)
        mode = "partial-delta"
    else:
        # No filters: use final cumulative snapshot
        result = all_snapshots[-1][1]
        mode = "cumulative"

    return {
        "path": jsonl_path,
        "model": model or "unknown",
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
        "cached_input_tokens": result.get("cached_input_tokens", 0),
        "reasoning_output_tokens": result.get("reasoning_output_tokens", 0),
        "total_tokens": result.get("total_tokens", 0),
        "snapshots": len(all_snapshots),
        "mode": mode,
    }


def estimate_cost(data: dict) -> Optional[float]:
    """Estimate USD cost from token counts."""
    model = data.get("model", "").lower()
    prices = None
    for key in PRICING:
        if key in model:
            prices = PRICING[key]
            break
    if not prices:
        prices = PRICING["gpt-4o"]
    return (
        data["input_tokens"] * prices["input"]
        + data["output_tokens"] * prices["output"]
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
        print("Usage: python3 extract-codex-tokens.py <path-to-rollout-jsonl|--latest> [--after TS] [--before TS] [--json]")
        print("")
        print("Task isolation: use --after/--before to compute delta between two token_count snapshots.")
        print("  TS can be ISO 8601 (2026-04-10T06:00:00) or epoch milliseconds.")
        print("")
        print("Without --after/--before: returns final cumulative total (entire session).")
        print("With --after/--before: returns delta = (snapshot at --before) - (snapshot before --after).")
        sys.exit(1)

    target = args["target"]
    if target == "--latest":
        path = find_latest_rollout()
    elif os.path.isfile(target):
        path = target
    else:
        print(f"Error: file not found: {target}")
        sys.exit(1)

    if not path:
        print("Error: no Codex session found")
        sys.exit(1)

    after = parse_time_filter(args["after"]) if args["after"] else None
    before = parse_time_filter(args["before"]) if args["before"] else None

    data = extract_tokens(path, after=after, before=before)

    if "error" in data:
        print(f"Error: {data['error']}")
        print(f"File: {data['path']}")
        sys.exit(1)

    cost = estimate_cost(data)

    if not args["json_out"]:
        print(f"Model:     {data['model']}")
        print(f"File:      {data['path']}")
        print(f"Snapshots: {data['snapshots']}")
        print(f"Mode:      {data['mode']}")
        if after or before:
            print(f"Filter:    after={args['after']} before={args['before']}")
        print()
        print(f"  input_tokens:       {data['input_tokens']:>10,}")
        print(f"  cached_input:       {data['cached_input_tokens']:>10,}")
        print(f"  output_tokens:      {data['output_tokens']:>10,}")
        print(f"  reasoning_tokens:   {data['reasoning_output_tokens']:>10,}")
        print(f"  total_tokens:       {data['total_tokens']:>10,}")
        print()
        if cost is not None:
            print(f"  Estimated cost:     ${cost:.4f}")

    if args["json_out"]:
        print(json.dumps({
            "input_tokens": data["input_tokens"],
            "output_tokens": data["output_tokens"],
            "cache_read_tokens": data["cached_input_tokens"],
            "cache_write_tokens": None,
            "total_tokens": data["total_tokens"],
            "estimated_cost_usd": round(cost, 4) if cost is not None else None,
            "model": data["model"],
            "mode": data["mode"],
        }, indent=2))


if __name__ == "__main__":
    main()
