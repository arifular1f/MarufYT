# Performance Profile (Phase 4.1)

## Limitation (exact)

No iPhone, no Instruments, and no iOS simulator are available in this environment (Windows host; the tweak builds only on GitHub Actions' Linux runners). Therefore **none of these were measured**: cold or warm launch, main-thread work, navigation or tab-switch latency, memory footprint or peak, CPU, image-cache residency or eviction, background CPU, request counts at runtime, battery. No before/after comparison exists and none is claimed.

## What is known without a device

| Fact | Source |
| --- | --- |
| Release library size 5,573,232 bytes (previous build 5,573,040): +192 bytes for the Phase 4.1 changes | measured on the two CI dylibs |
| Mini player, audio player and Now Playing no longer read artwork on the main thread; artwork cache bounded at 8 images / about 16 MB | code + `MAIN_THREAD_NETWORK_REPORT.md` |
| No repeating layout timer remains in the download card (Phase 3) | code |
| Repeating timers still present: mini-player 0.35 s tick while a library track is shown, sleep timers, player HUD hide timers, a 0.1 s gesture timer, and the opt-in capsule `CADisplayLink` | grep; not profiled |
| 47 observer registrations, all with reviewed lifetimes | `OBSERVER_LIFECYCLE_REPORT.md` |
| No `NSLog`; diagnostics log is append-only | code |

## Reproducible iPhone profiling checklist

Use a release (non-debug) build signed with your own certificate on the iPhone 15 Pro Max, one video app version at a time, airplane mode off, same account, 3 runs each, record median. Compare `1.1.4+marufyt.6` (Phase 4) with `.7` (Phase 4.1), and optionally with the stock YouTube IPA.

1. **Cold launch:** force-quit, then Instruments → App Launch (or `xctrace record --template "App Launch"`); record time to first frame of Home.
2. **Warm launch:** background for 10 s, relaunch; same template.
3. **Main-thread work:** Time Profiler for 60 s scrolling Home; export the heaviest main-thread symbols; turn on the Main Thread Checker and Hang detection.
4. **Navigation / tab switching:** Animation Hitches template; switch Home → Shorts → Subscriptions → Library 20 times; record hitch count and duration.
5. **Memory:** Allocations + Leaks for 10 minutes of normal use, then open and close the Downloads library, audio player and full player 20 times each; mark generations after each cycle; record the footprint at start, peak, and end, plus persistent controllers.
6. **Artwork path:** play 30 different audio downloads; confirm no main-thread hang in the Time Profiler and that the footprint plateaus (cache bound).
7. **CPU / background:** Activity Monitor template with the app backgrounded and audio playing for 5 minutes; and idle on Home for 5 minutes.
8. **Network count:** Network template or a proxy (mitmproxy, test account) for a 5-minute session with SponsorBlock on, once with Private Lookup on; count requests per host.
9. **Battery:** Energy Log for 30 minutes of identical playback per build; battery claims need several repeated runs and the same brightness and network.

Record the numbers in a table here with device, iOS build, date and run count. Until then this file contains no measurements.
