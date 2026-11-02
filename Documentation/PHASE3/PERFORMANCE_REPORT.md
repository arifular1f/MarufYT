# Performance Report (Phase 3)

**No profiling was performed.** There are no RAM, CPU, energy or launch measurements for this build, so none are claimed and no battery improvement is claimed. Instruments is not available in this environment. Status: **NOT TESTED**.

## Changes made (by inspection)

| Area | Change | Why it should help | Measured? |
| --- | --- | --- | --- |
| Layout polling | Download progress card's repeating 2 s timer removed; relayout on orientation change and app/scene activation | No background wakeups for layout | No |
| Diagnostics log | Appends one line with a file handle; rewrites only when over 512 KiB (trims to 75%). Previously read and rewrote the whole file for every line | Far less disk I/O during downloads | No |
| Glass defaults | Four glass presets and depth shadow no longer default on | Fewer blur/shadow layers in the default configuration | No |
| Animations | Springs removed from four overlays | Shorter animations | No |

## Reviewed and left as is

- **Image caches** are already bounded: DeArrow `countLimit = 160`, `totalCostLimit = 24 MiB`; audio queue info `countLimit = 400`; downloads metadata `countLimit = 64`.
- **Localization** already caches the active string table and reloads only when the language changes.
- **Remaining timers** (not removed): mini player 0.35 s tick (drives playback progress and re-parenting the card), player HUD timers, sleep timers, a 0.1 s gesture timer in `PlayerGestures.mm`, and a `CADisplayLink` for the opt-in capsule lens tracker. They were not profiled; the mini player tick also repositions the card and is a candidate for event-driven replacement later.

## Not claimed

Any number for memory, CPU, battery, launch time or frame rate.
