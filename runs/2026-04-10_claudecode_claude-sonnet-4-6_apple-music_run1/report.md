# Benchmark Report: apple-music-reference — claudecode (Sonnet 4.6) run1

**Date:** 2026-04-10
**Platform:** claudecode (Claude Code on staging devbox)
**Model:** Claude Sonnet 4.6
**Task:** Search Apple Music for "bohemian rhapsody queen", download 30s preview
**Result:** SUCCESS — 964 KB M4A preview

## Timing Summary

| Step | Time |
|------|------|
| search_apple_music (--search-only) | 0.611s |
| search_and_download_preview | 8.077s |
| **Total tool calls** | **8.688s** |
| **LLM overhead** | **17.407s** |
| **Wall total** | **26.095s** |

- LLM overhead: 66.7% of wall time
- Skill/tool execution: 33.3% of wall time

## Result

- Track: **Bohemian Rhapsody** by **Queen**
- Album: Greatest Hits I, II & III: The Platinum Collection
- Duration: 355s (full track)
- Preview: 30s M4A, 964 KB

## Observations

- **Fastest skill benchmarked so far:** 8.7s total tool time vs 36s (video-translation), 124s (music-beat-sync), 45s (video-captions).
- **LLM overhead dominates at 66.7%:** Because the skill itself is so fast, the fixed ~17s LLM context overhead becomes the majority of wall time. This is the inverse of music-beat-sync (18% LLM) where the skill dominates.
- **Search adds minimal overhead:** search-only (0.611s) vs search+download (8.077s) — the 7.5s delta is almost entirely the CDN preview download, not extra search cost.
- **Pure API skill:** zero CPU — just Apple Music search API + CDN download. No ffmpeg, no ML model, no file processing.
- **Consistent preview size:** 964 KB at 30s matches documented expectation (~964 KB).
