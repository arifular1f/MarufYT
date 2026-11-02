# Main-Thread and Network Report (Phase 4.1)

Phase 4 lead S-10: blocking waits after `NSURLSession` tasks. Every wait, request helper and main-thread file read was traced to its caller.

## Blocking waits (`dispatch_semaphore_wait`)

| File | Waits | Thread | Timeout | Verdict |
| --- | --- | --- | --- | --- |
| `DirectDownloader.mm` | 2 | Entered from `dispatch_async(global, USER_INITIATED)` (lines 359, 394); UI callbacks are posted back with `dispatch_async(main)` | 20–25 s style deadlines, `request timed out` error | **Investigated, not an issue** |
| `PlaylistDownloader.mm` | 2 | `YTKACEFetchFullPlaylist` runs the page loop and the auth probe inside a global-queue block | 10 s and 25 s | Not an issue. The auth probe waits on the host's authorizer callback from a background queue, so it cannot deadlock the main thread |
| `HLSPlayback.mm` | 1 | `YTKACEHLSFetchVisionThen` dispatches to a global queue before calling `YTKACEVisionVisitor()`; `ready` is returned on main | 12 s | Not an issue |
| `TVClient.mm` | 1 | `YTKACETVFetchPlayerResponse` starts with `dispatch_async(global)`; sole caller is `SABRDownloader` (background) | 20 s | Not an issue. The completion runs on that background queue; its only caller does not touch UI |
| `AiSList.mm` | 1 | Utility queue | 35 s | Not an issue |
| `YTKACEMediaImporter.mm` | 2 | `importURLs:` dispatches to a global queue | **None** (FFmpeg remux can be long) | **Confirmed but unresolved, low:** if the muxer never calls its completion the utility thread waits forever. Not changed: a timeout would cut off legitimate long remuxes. No hang has been observed |

## Main-thread file I/O: confirmed and fixed

`YTKACEMediaArtworkImage()` reads a sidecar `.jpg/.png` and, failing that, parses the media file's metadata through `AVURLAsset`. It was called on the main thread:

- `GlobalDownloadMiniPlayer -refresh`, on every playback change and app activation;
- `YTKACEAudioPlayerController` when the track changes;
- `YTKACEDownloadPlaybackSession -updateNowPlayingInfo`, on every playback change.

**Fix:** `MediaArtwork.mm` now has a bounded cache (8 images, about 16 MB, absence remembered, keyed by path and modification date), `YTKACEMediaArtworkCachedImage()` (cache only) and `YTKACEMediaArtworkImageAsync()` (utility queue, completion on main). The three sites use the cache and load once in the background; late results are ignored if the track has changed. The remaining direct call is inside the audio player's queue-info loader, which already runs on a global queue. Behaviour is the same except that artwork can appear a moment after the controls instead of blocking them.

Limit of the cache key: a replaced sidecar image with an unchanged media file keeps the old artwork until the app restarts (embedding artwork changes the media file's date, so that path refreshes).

## Other requests

- Images, captions and avatars: asynchronous `NSURLSession` tasks; HTTPS required since Phase 4 (`URLPolicy.h`); no UI update off the main thread was found (UI work in callbacks is dispatched to main).
- No synchronous `NSURLConnection` or `dataWithContentsOfURL:` on a remote URL. The `dataWithContentsOfURL:` calls are local files (diagnostics log trim, request seed, artwork, muxer) on background queues, apart from the artwork case fixed above.
- Concurrent request volume: playlist pages are fetched serially; SponsorBlock results are cached per video (128 entries). No change made.

## Tests

`Tests/test_concurrency_invariants.py` pins the six files that may contain a blocking wait and their counts, requires background dispatch in those files, forbids `DISPATCH_TIME_FOREVER` outside the muxer wait, and forbids synchronous artwork reads in the main-thread files.

**Not tested:** cancellation and timeout behaviour at runtime (needs network fault injection on a device); callback ordering. These are static guards, not behavioural tests. **Requires physical iPhone testing** with Instruments' Time Profiler or the Main Thread Checker while a playlist download and an audio track change run.
