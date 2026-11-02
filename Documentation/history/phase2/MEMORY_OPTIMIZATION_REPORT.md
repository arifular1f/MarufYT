# Memory review and changes

| Component | Before (source) | After (source) | Limits |
| --- | --- | --- | --- |
| DeArrow thumbnail NSCache | 160 entries, no memory cost budget | 160 entries plus 24 MiB totalCostLimit, decoded CGImage row bytes times height per insertion | Advisory eviction budget; not a process RAM ceiling |
| Download library metadata/thumbnail cache | No count/cost limits | 64 entries, 32 MiB totalCostLimit, decoded thumbnail cost | Dictionary/decoder/AVFoundation overhead not included |
| Download metadata queue | Three concurrent operations; weak controller callbacks | Same concurrency; pending operations cancelled on controller deallocation | In-flight synchronous AVFoundation operations may finish |
| Lens tracker | Weak lens, bounded timeout, pending completion | Off-window/inactive invalidation and pending completion release | Native private lens still needs allocation/leak profiling |
| Settings icon tiles | Existing NSCache limit 64 | Unchanged | No measured problem justifies another cache |

Files: Features/SponsorBlock/DeArrow.mm, Settings/YTKACEDownloadsController.mm,
Features/Navigation/TabBarHooks.mm. Both hosts use these components. Image cost
uses decoded pixels rather than compressed JPEG byte count; NSCache can evict
earlier under pressure. It can also briefly exceed its advisory limit. Cost
accounting does not change image selection, network responses or media contents.

Reviewed existing weak UI callbacks, metadata queue, observer deallocation,
download progress lifetime, bounded SponsorBlock cache and DeArrow in-flight sets.
No new observer or persistent media buffer was introduced. Downloads and playback
pipelines remain unchanged. This targeted source review is not a complete leak
proof, thread-safety proof or runtime heap audit.

Peak/steady RAM, 30-minute playback/navigation, background audio, large libraries,
memory warnings and allocation lifetime on both iPhone builds: **NOT TESTED**.
See PERFORMANCE_BEFORE_AFTER.md; no measured RAM savings are claimed.
