# Skill Performance Benchmark Round 2: PikaBot vs Claude Code (post-fix)

**Date:** 2026-04-09
**Test video:** charli-daily-vlog.mp4 (720x1280, 67.8s)
**What changed since Round 1:** ffmpeg stderr leak fix (`b6f4628`), skills installed fresh from CMS via subagent flow

## Platforms

| | PikaBot | Claude Code |
|--|---------|-------------|
| **Runtime** | Agent pod on EKS (dedicated vCPUs) | Staging devbox (shared EC2) |
| **LLM** | Claude with ~106K system prompt | Claude Opus 4.6 (1M context) |
| **Skill install** | CMS → download zip → subagent session | Latest git repo (already local) |
| **Output delivery** | `pika-upload-file` → CDN | Local disk (instant) |

---

## Round 2 Results

### With install (full e2e)

| Skill | PikaBot e2e | Claude Code e2e | CC faster by |
|-------|-------------|-----------------|--------------|
| video-captions | 311.8s | 140.7s | **2.2x** |
| music-beat-sync | 428.3s | 267.6s | **1.6x** |
| video-translation | 693.2s | 77.3s | **9.0x** |
| apple-music | 215.1s | 16.5s | **13.0x** |

### If skill already installed (subtract install tool time + estimated install LLM overhead ~100s)

| Skill | PikaBot (pre-installed) | Claude Code | CC faster by | Change |
|-------|------------------------|-------------|--------------|--------|
| video-captions | ~211s | 140.7s | **1.5x** | was 2.2x |
| music-beat-sync | ~328s | 267.6s | **1.2x** | was 1.6x |
| video-translation | ~593s | 77.3s | **7.7x** | was 9.0x |
| apple-music | ~115s | 16.5s | **7.0x** | was 13.0x |

Removing install narrows the gap but **Claude Code still wins every skill**. The remaining LLM overhead (136-538s) from skill execution turns alone still dominates PikaBot's wall time.

**Note:** video-translation and apple-music remain heavily lopsided because their install LLM overhead was a smaller fraction of total LLM overhead — the subagent session itself had long thinking gaps unrelated to install.

---

## Skill Download & Install Breakdown

In Round 2, PikaBot installs skills fresh from the Pika Staging Skill Hub CMS before each run. Claude Code uses the skill code directly from the local git repo — no install step.

### PikaBot install flow per skill

| Step | video-captions | music-beat-sync | video-translation | apple-music |
|------|---------------|-----------------|-------------------|-------------|
| CMS fetch (GET bundle URL) | 0.19s | 0.22s | 0.55s | 0.39s |
| Download zip + extract | 0.15s | 0.17s | 0.13s | 0.12s |
| Subagent session start | ~1s | ~1s | ~1s | ~1s |
| **Install total (tool time)** | **~1.3s** | **~1.4s** | **~1.7s** | **~1.5s** |

The install tool calls themselves are fast (~1.3-1.7s). But the **LLM turns around install** are expensive:

| Step | Estimated LLM overhead |
|------|----------------------|
| LLM reads prompt, decides to install | 10-15s |
| LLM composes CMS fetch command | 10-15s |
| LLM reads CMS response, composes extract command | 10-15s |
| LLM decides to spawn subagent | 10-15s |
| Subagent boots, LLM loads context + skills index | 30-60s |
| Subagent LLM reads task, decides first action | 10-15s |
| **Install LLM overhead (estimated)** | **80-135s** |

So the true cost of install is not the 1.5s of tool calls — it's the **80-135s of LLM thinking** around those calls. This is a major contributor to Round 2 being slower than Round 1 (where skills were pre-installed).

### Claude Code: no install step

Claude Code uses the skill scripts directly from `~/code/nova3-agent-skills/` (the local git repo, pulled to latest). No CMS fetch, no zip extract, no subagent. The LLM already has the skill usage instructions in memory, so it goes straight to execution.

| | PikaBot | Claude Code |
|--|---------|-------------|
| Install tool time | ~1.5s | 0s |
| Install LLM overhead | ~80-135s | 0s |
| **Total install cost** | **~82-137s** | **0s** |

This structural difference accounts for a significant chunk of the e2e gap, especially for fast skills like apple-music (where install overhead exceeds the skill runtime by 100x).

---

## The Overhead Breakdown

### PikaBot: where the time goes

| Skill | Install | Skill compute | Upload | LLM overhead | Wall total |
|-------|---------|---------------|--------|--------------|------------|
| video-captions | ~1.3s (<1%) | 53.6s (17%) | 21.1s (7%) | 236.6s (76%) | 311.8s |
| music-beat-sync | ~1.4s (<1%) | 144.2s (34%) | 1.8s (<1%) | 282.4s (66%) | 428.3s |
| video-translation | ~1.7s (<1%) | 31.0s (4%) | 22.3s (3%) | 638.2s (92%) | 693.2s |
| apple-music | ~1.5s (<1%) | 0.9s (<1%) | 48.3s (22%) | 164.4s (76%) | 215.1s |

### Claude Code: where the time goes

| Skill | Skill compute | Upload | LLM overhead | Wall total |
|-------|--------------|--------|--------------|------------|
| video-captions | 105.4s (75%) | 0s | 35.3s (25%) | 140.7s |
| music-beat-sync | 235.4s (88%) | 0s | 32.1s (12%) | 267.6s |
| video-translation | 50.3s (65%) | 0s | 27.0s (35%) | 77.3s |
| apple-music | 1.2s (7%) | 0s | 15.3s (93%) | 16.5s |

### The pattern

```
PikaBot time allocation:           Claude Code time allocation:

  LLM ████████████████████ 66-92%     Skill ██████████████████ 7-88%
  Skill ████████░░░░░░░░░ <1-34%     LLM ██████░░░░░░░░░░░░ 12-93%
  Upload ████░░░░░░░░░░░░ <1-22%     Upload ░░░░░░░░░░░░░░░░ 0%
```

PikaBot spends most time **thinking**. Claude Code spends most time **working**.

---

## Upload Variance Is Extreme

| Skill | File size | Upload time | KB/s |
|-------|-----------|-------------|------|
| music-beat-sync | 16.0MB | 1.84s | 8,913 |
| video-captions | 30.0MB | 21.06s | 1,461 |
| video-translation | 3.2MB | 22.25s | 144 |
| apple-music | 0.96MB | 48.34s | 20 |

Upload time is **completely uncorrelated with file size**. The smallest file (964KB) took the longest (48s). This suggests the bottleneck is in the `pika-upload-file` tool invocation or CDN endpoint variance, not bandwidth.

---

## Round 1 vs Round 2

| Skill | PikaBot R1 | PikaBot R2 | PikaBot R2 (no install) | CC R1 | CC R2 |
|-------|-----------|-----------|------------------------|-------|-------|
| video-captions | 371.4s | 311.8s | ~211s | 138.3s | 140.7s |
| music-beat-sync | 356.6s | 428.3s | ~328s | 315.8s | 267.6s |
| video-translation | ~105s | 693.2s | ~593s | 60.7s | 77.3s |
| apple-music | ~20s | 215.1s | ~115s | 16.1s | 16.5s |

### PikaBot R2 vs R1: install overhead is the difference

| Skill | R1 → R2 (raw) | R1 → R2 (no install) | Explanation |
|-------|---------------|---------------------|-------------|
| video-captions | 371→312 (**-16%**) | 371→211 (**-43%**) | ffmpeg fix helped; without install overhead, R2 is significantly faster |
| music-beat-sync | 357→428 (+20%) | 357→328 (**-8%**) | Raw R2 looks slower, but remove install and it's actually slightly faster |
| video-translation | 105→693 (+560%) | 105→593 (+465%) | Still much slower — subagent had 507s LLM gap unrelated to install |
| apple-music | 20→215 (+975%) | 20→115 (+475%) | Still much slower — LLM overhead dominates a sub-second skill |

**Key insight:** For CPU-heavy skills (video-captions, music-beat-sync), removing install makes R2 **faster than R1** — the ffmpeg stderr fix and consistent upload times paid off. For API-light skills (video-translation, apple-music), the subagent session itself introduced huge LLM thinking gaps that dwarf the install cost.

### Claude Code is consistent

All four skills within ~10-20% of Round 1. No structural change — same repo, same venv, same workflow.

---

## Key Findings

### 1. LLM overhead is 66-92% of PikaBot's wall time

Across all four skills, LLM thinking dominates. The 106K system prompt + subagent session flow creates a massive overhead that no skill optimization can overcome.

### 2. The ffmpeg stderr fix had minimal e2e impact

Video-captions improved 16% (371s → 312s), but LLM overhead increased from other factors (subagent flow). The fix likely eliminated the 111s spike from Round 1, but new overhead from the install flow offset the gains.

### 3. Upload is unpredictable and uncorrelated with file size

`pika-upload-file` latency ranges from 1.8s to 48.3s with no relationship to file size. This needs investigation — could be presigned URL generation, CDN cold starts, or tool invocation overhead.

### 4. Skill execution speed is not the bottleneck

PikaBot is genuinely 1.3-2.5x faster on skill execution (better CPU, in-cluster proxy). But when skills take 30-150s and overhead adds 160-638s, the CPU advantage is irrelevant.

### 5. Claude Code's structural advantages compound

| Advantage | Savings per run |
|-----------|----------------|
| No upload needed | 2-48s |
| No skill install needed | 1-2s direct, but 100-500s of LLM turns |
| Smaller LLM context → faster turns | 3-5s vs 10-15s per turn |
| Fewer LLM turns (batch tool calls) | 100-600s |
| **Total structural advantage** | **100-650s** |

---

## Recommendations (updated from Round 1)

### Priority 1: Reduce LLM turns for skill execution (CRITICAL)
The install + subagent + multi-step orchestration flow is the #1 bottleneck. A single "run this skill" tool that handles download → execute → upload in one shot would eliminate 4-8 LLM turns (40-120s each).

### Priority 2: Reduce system prompt size (HIGH)
106K prompt → 10-15s per turn. Cut to <50K → 5-8s per turn. Saves 30-60s per skill across 5-10 turns.

### Priority 3: Fix `pika-upload-file` variance (MEDIUM)
48s for 964KB is pathological. Investigate presigned URL generation latency and CDN endpoint health.

### Priority 4: Skip subagent for skill runs (MEDIUM)
The subagent session startup added 100-500s in overhead. If skills can run in the current session, this overhead disappears.
