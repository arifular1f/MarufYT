# Feature Regression Report (Phase 4)

Phase 4 changed one behaviour in code: an https-only check before fetching profile pictures, post images and caption files (`URLPolicy.h`). No feature was removed or disabled and no default changed.

## Evidence available

| Evidence | Result |
| --- | --- |
| `Tools/marufyt_checks.py` | 0 failures |
| Python tests and native layout-math tests (CI) | Pass |
| CI build of `236102f` | Success, 0 warnings |
| `verify_release.py` on both IPAs | 40/40 each; every YTKACE 1.1.4 class, selector and preference key still present except documented removals |
| Host audit 21.39.4 → 21.43.5 | 7 of 9 hook areas unchanged; Navigation and Liquid Glass differ by one selector each (optional glass modes only) |

## Per feature

"Static" = the code path is present and unchanged by Phase 4. No row was exercised on a device.

| Feature | Static | Device |
| --- | --- | --- |
| Google sign-in, account switching | Unchanged; URL scheme and keychain group handling intact | Not tested |
| Ad blocking | Unchanged | Not tested |
| SponsorBlock, DeArrow, AiSList | Unchanged (opt-in) | Not tested |
| Background audio, PiP | Unchanged; `audio` background mode kept | Not tested |
| Video / audio / playlist downloads, subtitles | Unchanged; playlist and transcript endpoints still HTTPS | Not tested |
| Playback speed, loop, sleep timer | Unchanged | Not tested |
| Shorts, feed, tab, top-bar customization | Unchanged | Not tested |
| Simple tab bar (default), optional Liquid Glass | Unchanged since Phase 3 | Not tested |
| Settings persistence | Unchanged | Not tested |
| Profile picture preview, post-image save, transcript export | **Touched**: now skip non-https URLs. YouTube normally supplies https, so no visible change is expected | Not tested |

Use `Documentation/PHASE3/DEVICE_TEST_RESULTS.md` as the checklist for the device pass.
