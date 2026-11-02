# Observer Lifecycle Report (Phase 4.1)

Question from Phase 4: 30 observer registrations against 6 removals. Every registration under `Tweak/` was traced (47 call sites in 23 files by the stricter count (17 block observers, 30 selector or KVO) in `Tests/test_concurrency_invariants.py`, which counts every `addObserver:` and `addObserverForName:`).

## Result

**Investigated, not an issue: no leak or duplicate registration was confirmed.** The gap between registrations and removals is explained by design, below. No code change was needed.

| Kind | Sites | Owner and lifetime | Removal | Verdict |
| --- | --- | --- | --- | --- |
| Selector observers on view controllers (`YTKACEDownloadsController`, `YTKACEAudioPlayerController`, `YTKACEDownloadPlayerController`) | registered in `viewDidLoad` / `observePlayback`, once per instance | the controller | `removeObserver:self` in `dealloc` (the "6 removals" are these deallocs). Selector observers are also dropped automatically on deallocation on current iOS | Not an issue |
| Selector observers on process-lifetime singletons (`GlobalDownloadMiniPlayer`, `DownloadProgressView`, `LoopControls`, `SleepTimerControls`, `SpeedControls`) | registered in `init` / `dispatch_once` | the singleton | never removed; live as long as the process by design | Not an issue |
| Block observers (`addObserverForName:`) | 17 | the process | tokens not stored (never removed) | Each sits behind a once-guard: `dispatch_once`, a flag, a nil check, or a constructor. All module installers run from the single `YTKACEInstallModules()` in `Entry.mm` |
| `ExtraDim` constructor, `RemoteSkip` constructor | 3 | the process | n/a | Run once at load |
| KVO: `AVPictureInPictureController pictureInPicturePossible` | 1 | `YTKACELibraryPiP` singleton | `detachController` (called before every re-attach) | Not an issue |
| KVO: `AVPlayerItem status` | 1 | `PiPControls` | `stopObservingItem` guarded by `observingItem` | Not an issue |
| Periodic time observers | 3 | download player, session | removed in `dealloc`; the session's `AVPlayer` is created once, so the remove call targets the same player | Not an issue |

Block observers capturing `self` strongly: none found (a regex test fails on any `self` inside an `addObserverForName:` block). Notification tokens: unused tokens are acceptable only because the observers are process-lifetime.

## One lifecycle detail worth knowing

`ShortsSessionLimit` and `SponsorHooks` keep their token in a static and check it for nil; the others rely on `dispatch_once`. All equivalent.

## Regression tests

`Tests/test_concurrency_invariants.py` (runs in CI):

- pins the reviewed observer count per file, so a new observer fails until it is reviewed;
- requires `removeObserver:self` plus `dealloc` in the three controller files;
- requires the once-guards above and a single call of each module installer;
- fails if a block observer references `self`.

## Not tested

Repeated opening and closing of the screens on a device (no instrumented run was possible). The tests are static: they guard the invariants, they do not execute UIKit. **Requires physical iPhone testing:** open and close the Downloads library, audio player and full player 20 times and watch memory in Instruments (Allocations, "Generation" marks) for retained controllers.
