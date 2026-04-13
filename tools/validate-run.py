#!/usr/bin/env python3
"""Validate a benchmark run directory: check result.json completeness and report.md pairing."""

import json
import sys
import os

def validate_json(data, path):
    """Check required fields and sanity of result.json."""
    errors = []
    warnings = []

    # Required top-level sections
    for section in ["meta", "task", "platform", "phases", "tokens", "cost", "totals"]:
        if section not in data:
            errors.append(f"Missing required section: {section}")

    if errors:
        return errors, warnings

    # meta
    meta = data["meta"]
    if not meta.get("date"):
        errors.append("meta.date is empty")
    if not meta.get("tester"):
        warnings.append("meta.tester is empty")

    # task
    task = data["task"]
    if not task.get("name"):
        errors.append("task.name is empty")
    if not task.get("purpose"):
        warnings.append("task.purpose is empty — describe what you're testing")
    if not task.get("expected_output"):
        warnings.append("task.expected_output is empty — describe what success looks like")

    # platform
    platform = data["platform"]
    valid_platforms = ["pikabot", "claudecode", "managed-claude-agent", "codex"]
    if not platform.get("name"):
        errors.append("platform.name is empty")
    elif platform["name"] not in valid_platforms:
        warnings.append(f"platform.name '{platform['name']}' not in standard list: {valid_platforms}")
    if not platform.get("llm_model"):
        warnings.append("platform.llm_model is empty")

    # totals
    totals = data["totals"]
    wall = totals.get("wall_total_s")
    tool = totals.get("tool_calls_s")
    llm = totals.get("llm_overhead_s")

    if wall is None:
        errors.append("totals.wall_total_s is required")
    else:
        if tool is not None and llm is not None:
            if wall < tool:
                errors.append(f"totals.wall_total_s ({wall}) < tool_calls_s ({tool}) — impossible")
            if wall < llm:
                errors.append(f"totals.wall_total_s ({wall}) < llm_overhead_s ({llm}) — impossible")

    # phase totals consistency
    if wall is not None:
        phases = data.get("phases", {})
        phase_sum = 0
        for phase_name in ["install", "asset_acquisition", "execution", "delivery"]:
            phase = phases.get(phase_name, {})
            pt = phase.get("total_s")
            if pt is not None:
                phase_sum += pt
        if phase_sum > 0 and phase_sum > wall * 1.02:  # 2% tolerance for rounding
            errors.append(
                f"Sum of phase total_s ({phase_sum:.1f}) > wall_total_s ({wall}) — "
                f"phases have overlapping or double-counted time"
            )

        # Warn if steps have timing data but phase total_s is null
        for phase_name in ["asset_acquisition", "execution", "delivery"]:
            phase = phases.get(phase_name, {})
            if phase.get("total_s") is None:
                has_sub_timing = False
                # Check if any sub-field has a value
                for k, v in phase.items():
                    if k in ("tokens", "notes", "total_s"):
                        continue
                    if isinstance(v, (int, float)) and v > 0:
                        has_sub_timing = True
                        break
                    if isinstance(v, list) and v:  # steps list
                        for step in v:
                            if isinstance(step, dict) and step.get("duration_s") is not None:
                                has_sub_timing = True
                                break
                if has_sub_timing:
                    warnings.append(
                        f"phases.{phase_name}.total_s is null but sub-timings exist — fill total_s for cross-platform comparison"
                    )

    # tokens
    tokens = data["tokens"]
    is_codex = platform.get("name") == "codex"
    if tokens.get("input_tokens") is None and tokens.get("output_tokens") is None:
        warnings.append("tokens: both input_tokens and output_tokens are null — fill if available")

    # total_tokens validation (platform-aware)
    if tokens.get("total_tokens") is not None:
        inp = tokens.get("input_tokens") or 0
        out = tokens.get("output_tokens") or 0
        cr = tokens.get("cache_read_tokens") or 0
        cw = tokens.get("cache_write_tokens") or 0
        if is_codex:
            # Codex: cache_read is a subset of input (not additive).
            # total_tokens should be >= input + output.
            if tokens["total_tokens"] < inp + out:
                warnings.append(
                    f"tokens.total_tokens ({tokens['total_tokens']}) < input + output ({inp + out}) — impossible for Codex"
                )
        else:
            # Claude family: cache_read/write are separate from input (additive).
            # total_tokens should equal input + output + cache_read + cache_write.
            component_sum = inp + out + cr + cw
            if component_sum > 0 and abs(tokens["total_tokens"] - component_sum) > component_sum * 0.02:
                warnings.append(
                    f"tokens.total_tokens ({tokens['total_tokens']}) != sum of components ({component_sum})"
                )

    # cost (platform-aware)
    cost = data["cost"]
    if not cost.get("model"):
        warnings.append("cost.model is empty — needed for cost calculation")
    if cost.get("estimated_cost_usd") is None:
        warnings.append("cost.estimated_cost_usd is null — calculate from tokens × price")
    elif tokens.get("input_tokens") is not None:
        inp = tokens.get("input_tokens") or 0
        out = tokens.get("output_tokens") or 0
        cr = tokens.get("cache_read_tokens") or 0
        cw = tokens.get("cache_write_tokens") or 0
        declared = cost["estimated_cost_usd"]

        if is_codex:
            # Codex: cached input is subset of input.
            # If cache_read_price declared: cost = (input - cached) × full + cached × discount + output × out
            # If no cache_read_price: cost = input × full + output × out (no discount applied)
            inp_price = cost.get("input_price_per_million") or 0
            out_price = cost.get("output_price_per_million") or 0
            cr_price = cost.get("cache_read_price_per_million")
            if cr_price is not None and cr_price > 0 and cr > 0:
                non_cached = inp - cr
                recomputed = (non_cached * inp_price + cr * cr_price + out * out_price) / 1_000_000
            else:
                # No cache discount declared — simple formula
                recomputed = (inp * inp_price + out * out_price) / 1_000_000
            if abs(recomputed - declared) > 0.02:
                warnings.append(
                    f"cost.estimated_cost_usd ({declared}) != recomputed for Codex ({recomputed:.4f})"
                )
        else:
            # Claude family: additive cache pricing
            inp_price = cost.get("input_price_per_million") or 0
            out_price = cost.get("output_price_per_million") or 0
            cr_price = cost.get("cache_read_price_per_million") or 0
            cw_price = cost.get("cache_write_price_per_million") or 0
            recomputed = (inp * inp_price + out * out_price + cr * cr_price + cw * cw_price) / 1_000_000
            if abs(recomputed - declared) > 0.02:
                if (cr > 0 or cw > 0) and cr_price == 0 and cw_price == 0:
                    warnings.append(
                        f"cost.estimated_cost_usd ({declared}) includes cache tokens but "
                        f"cache pricing not declared — cost is not reproducible"
                    )
                else:
                    warnings.append(
                        f"cost.estimated_cost_usd ({declared}) != recomputed ({recomputed:.4f})"
                    )

    return errors, warnings


def validate_report(run_dir, data):
    """Check that report.md exists and has basic consistency with result.json."""
    errors = []
    warnings = []

    report_path = os.path.join(run_dir, "report.md")
    if not os.path.exists(report_path):
        errors.append("report.md not found — each run must have a paired report")
        return errors, warnings

    with open(report_path, "r") as f:
        content = f.read()

    if len(content.strip()) < 50:
        errors.append("report.md is too short (< 50 chars) — add meaningful content")
        return errors, warnings

    # Check key info present in report
    date = data.get("meta", {}).get("date", "")
    platform = data.get("platform", {}).get("name", "")
    task_name = data.get("task", {}).get("name", "")

    if date and date not in content:
        warnings.append(f"report.md doesn't mention the date ({date})")
    if platform and platform not in content.lower():
        warnings.append(f"report.md doesn't mention the platform ({platform})")
    if task_name and task_name not in content.lower():
        warnings.append(f"report.md doesn't mention the task ({task_name})")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-run.py <path/to/result.json>")
        print("       python validate-run.py <path/to/run-directory/>")
        sys.exit(1)

    target = sys.argv[1]

    # Accept either a JSON file or a directory
    if os.path.isdir(target):
        json_path = os.path.join(target, "result.json")
        run_dir = target
    else:
        json_path = target
        run_dir = os.path.dirname(target)

    if not os.path.exists(json_path):
        print(f"ERROR: {json_path} not found")
        sys.exit(1)

    with open(json_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON — {e}")
            sys.exit(1)

    # Validate JSON
    json_errors, json_warnings = validate_json(data, json_path)

    # Validate report
    report_errors, report_warnings = validate_report(run_dir, data)

    errors = json_errors + report_errors
    warnings = json_warnings + report_warnings

    # Print results
    if errors:
        print(f"\n{len(errors)} ERROR(s):")
        for e in errors:
            print(f"  x {e}")

    if warnings:
        print(f"\n{len(warnings)} WARNING(s):")
        for w in warnings:
            print(f"  ! {w}")

    if not errors and not warnings:
        print("OK — all checks passed")

    if not errors and warnings:
        print(f"\nPASSED with {len(warnings)} warning(s)")

    if errors:
        print(f"\nFAILED — fix {len(errors)} error(s) before committing")
        sys.exit(1)


if __name__ == "__main__":
    main()
