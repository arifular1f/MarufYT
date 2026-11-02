# Performance Report (Phase 4)

**No profiling was possible** (no device, no Instruments). There are no RAM, CPU, FPS, startup or battery numbers, and none are claimed. Everything below is a static review. Status: measurements **Not tested**.

## Review results

| Requirement | Result |
| --- | --- |
| No polling timers for layout | Phase 3 removed the download card's 2 s timer. Remaining repeating timers: mini-player 0.35 s tick (progress and re-parenting), sleep timers, player HUD hide timers, `PlayerGestures` 0.1 s, and a `CADisplayLink` for the opt-in capsule lens tracker. They are tied to visible features and invalidated when those hide, but were not profiled |
| Bounded caches | DeArrow images: 160 items / 24 MiB cost; audio queue info 400; downloads metadata 64; AiSList lists ≤ 8 MiB on disk. No unbounded cache was found |
| Observers | 30 `addObserver:` sites vs 6 `removeObserver` sites. Most are process-lifetime singletons registered once; duplicates and leaks **not proven absent**: Needs investigation |
| Release logging | No `NSLog`. Diagnostics log is append-only, size-capped (512 KiB, trimmed to 75%), and writes on a background queue |
| Disk I/O on main thread | The log runs on its own queue. `dataWithContentsOfURL:` appears in download/muxer/artwork code (background contexts expected); not traced exhaustively: Needs investigation |
| Blocking waits | `dispatch_semaphore_wait` in 5 network helpers (S-10 in `SECURITY_AUDIT.md`): caller threads not proven |
| Animation / rendering | Simple default (no blur or lens), springs removed from default-visible overlays in Phase 3, Reduce Motion honoured |
| Unnecessary network requests | SponsorBlock, DeArrow and AiSList are opt-in (no registered default); caches avoid repeat requests per video |

## Changes in Phase 4

None for performance. Phase 3's changes stand; adding unmeasured tuning would risk features (SponsorBlock, Downloads, PiP, background audio) for unproven benefit.

## What to measure next

Cold-start time, memory after 10 minutes of browsing and after a download, CPU while idle on the Home feed, energy log with Normal Home Layout on/off. Use Instruments on a device and record the numbers in this file.
